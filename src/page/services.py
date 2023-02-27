from page.models import Tag


class TagService:
    @staticmethod
    def process_tags(request) -> list:
        """
        Add tags ids to the tags_id list. If tag does not exist, the method
        creates a new tag and add its id to the tags_id list. Returns list
        with tag ids.
        """
        tags_id = []

        if 'tags' in request.data:
            tags = request.data.pop('tags')
            existing_tags = Tag.objects.filter(name__in=tags)
            for tag in existing_tags:
                tags_id.append(tag.id)
                tags.remove(tag.name)

            for tag in tags:
                new_tag = Tag.objects.create(name=tag)
                new_tag.save()
                tags_id.append(new_tag.id)

        return tags_id

