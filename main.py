import functions_framework
from flask import jsonify
from google.cloud import vision_v1
from google.cloud.vision_v1 import types

@functions_framework.http
def detect_nsfw(request):
    if request.method != 'POST':
        return jsonify({'error': 'method not allowed'}), 405

    if 'file' not in request.files:
        return jsonify({'error': 'no file provided'}), 400
    
    try:
        content = request.files['file'].read()

        client = vision_v1.ImageAnnotatorClient()
        image = types.Image(content=content)

        response = client.safe_search_detection(image=image)
        safe_search = response.safe_search_annotation

        likelihood_name = (
            "UNKNOWN",
            "VERY_UNLIKELY",
            "UNLIKELY",
            "POSSIBLE",
            "LIKELY",
            "VERY_LIKELY",
        )

        nsfw_thresholds = {
            'adult': vision_v1.Likelihood.VERY_LIKELY,
            'violence': vision_v1.Likelihood.LIKELY,
            'racy': vision_v1.Likelihood.VERY_LIKELY
        }

        is_nsfw = any(
            getattr(safe_search, category) >= threshold
            for category, threshold in nsfw_thresholds.items()
        )

        return jsonify({
            'is_nsfw': is_nsfw,
            'details': {
                'adult': likelihood_name[safe_search.adult],
                'violence': likelihood_name[safe_search.violence],
                'racy': likelihood_name[safe_search.racy],
                'medical': likelihood_name[safe_search.medical],
                'spoof': likelihood_name[safe_search.spoof]
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500