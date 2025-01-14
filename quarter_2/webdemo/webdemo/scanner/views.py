from django.shortcuts import render
from .forms import ImageUploadForm
from backend_poc import extract_img, validate
import os
import tempfile

def index(request):
    path = os.path.dirname(os.path.abspath(__file__))
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = request.FILES['image']

            try:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as tmp:
                    for chunk in uploaded_image.chunks():
                        tmp.write(chunk)
                    tmp.flush()

                    data = extract_img(tmp.name)
                    result = validate(os.path.join(path, "model.xz"), data)

                verdict = "Safe" if result == 0 else "Potential Quishing content detected!"
                return render(request, 'scanner/result.html', {'verdict': verdict})

            except Exception as e:
                error_message = str(e)

                if "com.google.zxing.NotFoundException" in error_message:
                    user_error = "The provided image does not contain a QR code."
                elif "com.google.zxing.ChecksumException" in error_message:
                    user_error = "The QR code is damaged or not decodable."
                else:
                    user_error = "Error processing the image: An unexpected error occurred."

                return render(request, 'scanner/index.html', {
                    'form': form,
                    'error': user_error
                })
        else:
            return render(request, 'scanner/index.html', {
                'form': form,
                'error': 'Invalid form data'
            })
    else:
        return render(request, 'scanner/index.html', {'form': ImageUploadForm()})

