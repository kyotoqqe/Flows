#temporary
from src.core.domain.value_obj import Image

class ImageClenupService:
    
    @staticmethod
    def _check_usage(image: Image):
        if image.ref_count == 0:
            return False
        return True