from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .utils import get_roles
from .models import ScriptDetail, Script


class ScriptOwnerPermission(IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        domain = view.kwargs['domain']
        fid = view.kwargs['fid']
        lid = view.kwargs['lid']
        tid = view.kwargs['tid']
        vid = view.kwargs['vid']
        if Script.objects.filter(domain=domain, foss_id=fid, language_id=lid, tutorial_id=tid, versionNo=vid, status=True).exists():
            return True
        if request.user.is_authenticated:
            return is_Contributor(domain, fid, lid, request.user.username) \
                or is_DomainReviewer(domain, fid, lid, request.user.username) \
                or is_QualityReviewer(domain, fid, lid, request.user.username)
        return False

    def has_object_permission(self, request, view, obj):
        obj.user == request.user


class ScriptModifyPermission(IsAuthenticatedOrReadOnly):
    def has__permission(self, request, view):
        obj = ScriptDetail.objects.get(pk=view.kwargs['script_detail_id'])
        domain = obj.script.domain
        fid = obj.script.fid
        lid = obj.script.lid
        if request.user.is_authenticated:
            return obj.script.user == request.user \
                or is_Contributor(domain, fid, lid, request.user.username) \
                or is_DomainReviewer(domain, fid, lid, request.user.username) \
                or is_QualityReviewer(domain, fid, lid, request.user.username)
        return False


class PublishedScriptPermission(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            domain = view.kwargs['domain']
            fid = view.kwargs['fid']
            lid = view.kwargs['lid']
            return is_Contributor(domain, fid, lid, request.user.username) \
                or is_DomainReviewer(domain, fid, lid, request.user.username) \
                or is_QualityReviewer(domain, fid, lid, request.user.username)
        return False


class ReviewScriptPermission(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            domain = view.kwargs['domain']
            fid = view.kwargs['fid']
            lid = view.kwargs['lid']
            return is_DomainReviewer(domain, fid, lid, request.user.username) \
                or is_QualityReviewer(domain, fid, lid, request.user.username)
        return False


class CommentOwnerPermission(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated


class CanCommentPermission(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return not obj.script.status


class CanRevisePermission(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return not obj.script.status


def is_Contributor(domain, fid, lid, username):
    roles = get_roles(domain, fid, lid, username)
    return 'Contributor' in roles


def is_DomainReviewer(domain, fid, lid, username):
    roles = get_roles(domain, fid, lid, username)
    return 'Domain-Reviewer' in roles


def is_QualityReviewer(domain, fid, lid, username):
    roles = get_roles(domain, fid, lid, username)
    return 'Quality-Reviewer' in roles
