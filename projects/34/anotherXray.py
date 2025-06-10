import skimage
import torch
import torch.nn.functional as F
import torchvision
import torchvision.transforms
import torchxrayvision as xrv

# Load the model
model = xrv.models.DenseNet(weights="densenet121-res224-all")
model.eval()

# Load and preprocess the local image
img = skimage.io.imread('rml_atelect.jpg')
img = xrv.datasets.normalize(img, 255)

# Check that images are 2D arrays
if len(img.shape) > 2:
    img = img[:, :, 0]
if len(img.shape) < 2:
    print("error, dimension lower than 2 for image")

# Add color channel
img = img[None, :, :]

transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop()])

img = transform(img)

# Get predictions
with torch.no_grad():
    img = torch.from_numpy(img).unsqueeze(0)
    preds = model(img).cpu()
    output = {
        k: float(v)
        for k, v in zip(xrv.datasets.default_pathologies, preds[0].detach().numpy())
    }

# Print predictions with percentages
print("\nX-ray Analysis Results:")
print("-" * 30)
for condition, probability in output.items():
    percentage = probability * 100
    print(f"{condition}: {percentage:.1f}%")
