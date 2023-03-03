from rest_framework import serializers

from core.services import LocalstackManager

ALLOWED_IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg', 'bmp', 'gif')


class ImageInternalValueMixin:
    def to_internal_value(self, data):
        if 'image' in data:
            serializer = ImageSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            image_url = serializer.save(instance=self.instance)
            data['image'] = image_url
        return super().to_internal_value(data)


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

    def save(self, instance=None, **kwargs):
        key = LocalstackManager.upload_file(
            file=self.validated_data['image']
        )
        image_url = LocalstackManager.create_object_url(key)
        if instance:
            LocalstackManager.delete_file(instance.image)
        return image_url
