class PostService:
    @staticmethod
    def toggle_like(request, post):
        if post.liked_by.filter(id=request.user.id).exists():
            post.liked_by.remove(request.user)
            message = {'status': f'Post {post.id} was unliked by you'}
        else:
            post.liked_by.add(request.user)
            message = {'status': f'Post {post.id} was liked by you'}
        return message
