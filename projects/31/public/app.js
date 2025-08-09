(() => {
  const chat = document.getElementById('chat');
  const micBtn = document.getElementById('micBtn');
  const stopBtn = document.getElementById('stopBtn');
  const textInput = document.getElementById('textInput');
  const sendBtn = document.getElementById('sendBtn');

  const State = {
    Idle: 'Idle',
    AwaitingId: 'AwaitingId',
    AwaitingConfirmation: 'AwaitingConfirmation',
  };

  let currentState = State.AwaitingId;
  let candidateNationalId = null;

  function appendMessage(role, text) {
    const row = document.createElement('div');
    row.className = `message ${role}`;
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;
    row.appendChild(bubble);
    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;
  }

  function speak(text) {
    if (!('speechSynthesis' in window)) return;
    const utter = new SpeechSynthesisUtterance(text);
    const voices = window.speechSynthesis.getVoices();
    const arVoice = voices.find(v => (v.lang || '').toLowerCase().startsWith('ar'));
    if (arVoice) utter.voice = arVoice;
    utter.lang = arVoice?.lang || 'ar-SA';
    utter.rate = 1;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);
  }

  // Load voices first time on some browsers
  window.speechSynthesis?.addEventListener('voiceschanged', () => {});

  function normalizeArabicIndicDigits(text) {
    // Map Arabic-Indic digits to ASCII
    const map = {
      '٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9',
      '۰':'0','۱':'1','۲':'2','۳':'3','۴':'4','۵':'5','۶':'6','۷':'7','۸':'8','۹':'9'
    };
    return text.replace(/[٠-٩۰-۹]/g, d => map[d] || d);
  }

  function extractDigits(text) {
    const normalized = normalizeArabicIndicDigits(text);
    const digits = normalized.replace(/[^0-9]/g, '');
    return digits;
  }

  function fmtDateArabic(iso) {
    try {
      const d = new Date(iso);
      return new Intl.DateTimeFormat('ar-EG', { day: 'numeric', month: 'long', year: 'numeric' }).format(d);
    } catch {
      return iso;
    }
  }

  function confirmIdFlow(id) {
    candidateNationalId = id;
    currentState = State.AwaitingConfirmation;
    const msg = `سمعت الرقم ${id}. هل هذا صحيح؟ قل نعم أو لا.`;
    appendMessage('bot', msg);
    speak(msg);
  }

  async function fetchPersonById(id) {
    const res = await fetch(`/api/people/${id}`);
    if (!res.ok) {
      throw new Error('not_found');
    }
    return res.json();
  }

  async function handleConfirmedId(id) {
    try {
      const person = await fetchPersonById(id);
      const birth = fmtDateArabic(person.birth);
      const reply = `الرقم صحيح. الاسم: ${person.name}. تاريخ الميلاد: ${birth}${person.gender ? `، الجنس: ${person.gender}` : ''}${person.city ? `، المدينة: ${person.city}` : ''}.`;
      appendMessage('bot', reply);
      speak(reply);
      currentState = State.AwaitingId;
      candidateNationalId = null;
    } catch (e) {
      const reply = 'عذرًا، لم أجد بيانات لهذا الرقم. حاول مرة أخرى.';
      appendMessage('bot', reply);
      speak(reply);
      currentState = State.AwaitingId;
      candidateNationalId = null;
    }
  }

  function startRecognition() {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
      const msg = 'المتصفح لا يدعم التعرف على الصوت. الرجاء استخدام كروم أو متصفح يدعم هذه الميزة.';
      appendMessage('bot', msg);
      speak(msg);
      return null;
    }
    const recognition = new Recognition();
    recognition.lang = 'ar-SA';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    return recognition;
  }

  function handleTextInput(text) {
    const t = text.trim();
    if (!t) return;
    appendMessage('user', t);

    if (currentState === State.AwaitingConfirmation) {
      const normalized = t.replace(/[\u064B-\u0652]/g, '').toLowerCase();
      const yesWords = ['نعم', 'ايوه', 'أيوه', 'ايوا', 'أيوا', 'صح', 'تمام', 'yes'];
      const noWords = ['لا', 'كلا', 'غلط', 'مو', 'مش', 'no'];
      if (yesWords.some(w => normalized.includes(w))) {
        handleConfirmedId(candidateNationalId);
        return;
      }
      if (noWords.some(w => normalized.includes(w))) {
        const msg = 'حسنًا، قل الرقم مرة أخرى.';
        appendMessage('bot', msg);
        speak(msg);
        currentState = State.AwaitingId;
        candidateNationalId = null;
        return;
      }
      // fallthrough: maybe they said a new number
    }

    const digits = extractDigits(t);
    if (digits.length >= 8) {
      confirmIdFlow(digits);
    } else {
      const msg = 'لم أتعرف على رقم وطني صالح. يرجى قول أو كتابة الرقم كاملاً.';
      appendMessage('bot', msg);
      speak(msg);
    }
  }

  // Wire UI
  sendBtn.addEventListener('click', () => {
    handleTextInput(textInput.value);
    textInput.value = '';
  });
  textInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      handleTextInput(textInput.value);
      textInput.value = '';
    }
  });

  let recognitionInstance = null;

  micBtn.addEventListener('click', () => {
    if (recognitionInstance) return;
    recognitionInstance = startRecognition();
    if (!recognitionInstance) return;
    micBtn.classList.add('recording');
    micBtn.disabled = true;
    stopBtn.disabled = false;

    recognitionInstance.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map(r => r[0]?.transcript || '')
        .join(' ');
      appendMessage('user', transcript);

      if (currentState === State.AwaitingConfirmation) {
        const normalized = transcript.replace(/[\u064B-\u0652]/g, '').toLowerCase();
        const yesWords = ['نعم', 'ايوه', 'أيوه', 'ايوا', 'أيوا', 'صح', 'تمام', 'yes'];
        const noWords = ['لا', 'كلا', 'غلط', 'مو', 'مش', 'no'];
        if (yesWords.some(w => normalized.includes(w))) {
          handleConfirmedId(candidateNationalId);
          return;
        }
        if (noWords.some(w => normalized.includes(w))) {
          const msg = 'حسنًا، قل الرقم مرة أخرى.';
          appendMessage('bot', msg);
          speak(msg);
          currentState = State.AwaitingId;
          candidateNationalId = null;
          return;
        }
      }

      const digits = extractDigits(transcript);
      if (digits.length >= 8) {
        confirmIdFlow(digits);
      } else {
        const msg = 'لم أتعرف على رقم وطني صالح. يرجى قول الرقم كاملاً.';
        appendMessage('bot', msg);
        speak(msg);
      }
    };

    recognitionInstance.onerror = () => {
      const msg = 'حدث خطأ في التعرف على الصوت. حاول مرة أخرى.';
      appendMessage('bot', msg);
      speak(msg);
    };

    recognitionInstance.onend = () => {
      micBtn.classList.remove('recording');
      micBtn.disabled = false;
      stopBtn.disabled = true;
      recognitionInstance = null;
    };

    recognitionInstance.start();
  });

  stopBtn.addEventListener('click', () => {
    try { recognitionInstance?.stop(); } catch {}
  });

  // Greeting
  const greeting = 'أهلًا بك! قل: رقمي الوطني ثم الأرقام. على سبيل المثال: 9921010143. بعد ذلك سأؤكد لك وأقرأ البيانات.';
  appendMessage('bot', greeting);
  speak(greeting);
})(); 