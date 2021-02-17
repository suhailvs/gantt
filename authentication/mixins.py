from django.contrib.auth.mixins import UserPassesTestMixin


class CreatorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_creator

