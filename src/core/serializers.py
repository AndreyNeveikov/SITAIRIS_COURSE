from rest_framework import serializers

from core.services import LocalstackManager


ALLOWED_IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg', 'bmp', 'gif')


class ImageSerializer(serializers.Serializer):  # noqa
    image_file = serializers.FileField()

    @staticmethod
    def validate_image(image):
        extension = image.name.rsplit('.')[-1]
        if extension.lower() not in ALLOWED_IMAGE_EXTENSIONS:
            raise serializers.ValidationError(
                {'error': 'Invalid uploaded image type.'}
            )
        return image

    def save(self, **kwargs):
        key = LocalstackManager.upload_file(
            file=self.validated_data['image_file']
        )
        image_url = LocalstackManager.create_object_url(key)
        instance = kwargs.get('instance')
        if instance:
            LocalstackManager.delete_file(instance.image)

        return image_url
