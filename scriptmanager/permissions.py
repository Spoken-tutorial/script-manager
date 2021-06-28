from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .utils import get_roles
from .models import ScriptDetail

class ScriptOwnerPermission(IsAuthenticatedOrReadOnly):
  def has_permission(self, request, view):
    if request.user.is_authenticated:
      domain = self.kwargs['domain']
      fid = self.kwargs['fid']
      lid = self.kwargs['lid']
      tid = self.kwargs['tid']
      return  is_Contributor(domain, fid, lid, tid) or is_DomainReviewer(domain, fid, lid, tid) or is_QualityReviewer(domain, fid, lid, tid)
    return False
    
  def has_object_permission(self, request, view, obj):
    obj.user == request.user

class ScriptModifyPermission(IsAuthenticatedOrReadOnly):
  def has_permission(self, request, view):
    if request.user.is_authenticated:
      domain = self.kwargs['domain']
      fid = self.kwargs['fid']
      lid = self.kwargs['lid']
      tid = self.kwargs['tid']
      return  is_Contributor(domain, fid, lid, tid) or is_DomainReviewer(domain, fid, lid, tid) or is_QualityReviewer(domain, fid, lid, tid)
    return False
      
class PublishedScriptPermission(IsAuthenticatedOrReadOnly):
    
  def has_object_permission(self, request, view, obj):
    if request.user.is_authenticated:
      domain = self.kwargs['domain']
      fid = self.kwargs['fid']
      lid = self.kwargs['lid']
      tid = self.kwargs['tid']
      return  is_DomainReviewer(domain, fid, lid, tid) or is_QualityReviewer(domain, fid, lid, tid)
    return False
  
class ReviewScriptPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    if request.user.is_authenticated:
      domain = self.kwargs['domain']
      fid = self.kwargs['fid']
      lid = self.kwargs['lid']
      tid = self.kwargs['tid']
      return  is_DomainReviewer(domain, fid, lid, tid) or is_QualityReviewer(domain, fid, lid, tid)
    return False


class CommentOwnerPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    if request.user.is_authenticated:
      domain = self.kwargs['domain']
      fid = self.kwargs['fid']
      lid = self.kwargs['lid']
      tid = self.kwargs['tid']
      return  is_Contributor(domain, fid, lid, tid) or is_DomainReviewer(domain, fid, lid, tid) or is_QualityReviewer(domain, fid, lid, tid) or obj.user == request.user
    return False
    

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