from core.tasks import unblock_page_at_specified_date
from page.models import Tag


class TagService:
    @staticmethod
    def process_tags(data) -> list:
        """
        Add tags ids to the tags_id list. If tag does not exist, the method
        creates a new tag and add its id to the tags_id list. Returns list
        with tag ids.
        """
        tags_id = []

        if 'tags' in data:
            tags = data.pop('tags')
            existing_tags = Tag.objects.filter(name__in=tags)
            for tag in existing_tags:
                tags_id.append(tag.id)
                tags.remove(tag.name)

            for tag in tags:
                new_tag = Tag.objects.create(name=tag)
                new_tag.save()
                tags_id.append(new_tag.id)

        return tags_id


class PageService:
    @staticmethod
    def toggle_follow_status(request, page) -> dict:
        """
        Manage followers and follow requests. Toggle page follow status.
        """
        message = {}
        if request.user not in (*page.followers.all(),
                                *page.follow_requests.all()):
            if page.is_private:
                page.follow_requests.add(request.user)
                message = {'status': 'Follow request successfully send.'}
            elif not page.is_private:
                page.followers.add(request.user)
                message = {'status': 'Now you follow this page.'}
        else:
            page.follow_requests.remove(request.user)
            page.followers.remove(request.user)
            message = {'status': 'You are not longer follow this page'}

        return message

    @staticmethod
    def unblock_page_task(page):
        """
        Run celery task to unblock page at specified date.
        """
        unblock_page_at_specified_date.apply_async(args=[page.id],
                                                   eta=page.unblock_date)

    @staticmethod
    def get_block_status_message(page) -> dict:
        """
        Return page block status message.
        """
        message = {'status': {'page': page.id,
                              'blocked': page.is_blocked,
                              'unblock date': page.unblock_date}
                   }

        return message
