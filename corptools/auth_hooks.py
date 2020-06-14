from allianceauth.services.hooks import MenuItemHook, UrlHook
from django.utils.translation import ugettext_lazy as _
from allianceauth import hooks
from . import urls


class MemberAudit(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self,
                              _('Member Audit'),
                              'far fa-eye fa-fw',
                              'corptools:view',
                              navactive=['corptools:'])

    def render(self, request):
        if request.user.has_perm('corptools.view_characteraudit'):
            return MenuItemHook.render(self, request)
        return ''

#class Structures(MenuItemHook):
#    def __init__(self):
#        MenuItemHook.__init__(self,
#                              _('Structures'),
#                              'fa fa-building fa-fw',
#                              'corptools:view',
#                              navactive=['corptools:'])

    #def render(self, request):
    #    if request.user.has_perm('View Structures Role'):
    #        return MenuItemHook.render(self, request)
    #    return ''

#class Moons(MenuItemHook):
#    def __init__(self):
#        MenuItemHook.__init__(self,
#                              _('Moon Timers'),
#                              'fa fa-moon-o fa-fw',
#                              'corptools:view',
#                              navactive=['corptools:'])

#    def render(self, request):
#        if request.user.has_perm('View Moon Role'):
#            return MenuItemHook.render(self, request)
#        return ''


#@hooks.register('menu_item_hook')
#def register_menu():
#    return Structures()

#@hooks.register('menu_item_hook')
#def register_menu():
#    return Moons()

@hooks.register('menu_item_hook')
def register_menu():
    return MemberAudit()

@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'corptools', r'^corptools/')
