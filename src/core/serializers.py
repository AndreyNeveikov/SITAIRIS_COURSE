from rest_framework import serializers

from core.services import LocalstackManager


ALLOWED_IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg', 'bmp', 'gif')


class ImageSerializer(serializers.Serializer):  # noqa
    image = serializers.FileField()

    @staticmethod
    def validate_image(image):
        extension = image.name.rsplit('.')[-1]
        if extension.lower() not in ALLOWED_IMAGE_EXTENSIONS:
            raise serializers.ValidationError(
                {'error': 'Invalid uploaded image type.'}
            )
        return image

    def save(self, **kwargs):
        key = LocalstackManager.upload_file(file=self.validated_data['image'])
        image_url = LocalstackManager.create_presigned_url(key)
        return image_url
