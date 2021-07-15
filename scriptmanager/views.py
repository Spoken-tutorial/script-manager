from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Script,ScriptDetail,Comment
from .serializers import ScriptDetailSerializer,ScriptSerializer,CommentSerializer,ReversionSerializer, ScriptListSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_payload_handler as default_jwt_payload_handler
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from reversion.models import Version
import os
from django.core.files.storage import FileSystemStorage
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import time
from .permissions import is_Contributor,is_DomainReviewer,is_QualityReviewer
import uuid
import subprocess 
from .permissions import ScriptOwnerPermission, ScriptModifyPermission, PublishedScriptPermission, ReviewScriptPermission, CommentOwnerPermission, CanCommentPermission, CanRevisePermission
from django.utils import timezone
from .utils import get_all_foss_languages, get_all_tutorials, get_tutorial_details

def custom_jwt_payload_handler(user):
  payload = default_jwt_payload_handler(user)

  #payload['is_domainreviewer'] = is_DomainReviewer(user)
  #payload['is_qualityreviewer'] = is_QualityReviewer(user)

  return payload

def index(request):
  token = ''
  if request.user.is_authenticated:
    jwt_payload_handler  =  api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler  =  api_settings.JWT_ENCODE_HANDLER
    payload  =  jwt_payload_handler(request.user)
    token  =  jwt_encode_handler(payload) 
  
  return render(request, 'scriptmanager/index.html', {'token': token})
  

class FossLanguageList(generics.ListAPIView):

  def get(self, request):
    data = get_all_foss_languages()
    return Response({ 'data':  data}, status=200)


class TutorialDetailList(generics.ListAPIView):

  def get(self, request, *args, **kwargs):
    tutorials = get_all_tutorials(self.kwargs['domain'], self.kwargs['fid'], self.kwargs['lid'])
    if tutorials:
      for k, v in enumerate(tutorials['tutorials']):
        script_exist, script = self.get_script_exist(v['id'])
        v['script_status'] = script_exist
        v['published'] =  script.status if script_exist else False
        if script_exist:
          v['published_by'] = script.published_by.username if script.published_by else None
        v['published_on'] = script.published_on if script_exist else None
        if script_exist:
          v['created_by'] = script.user.username if script.user else None
        v['suggested_title'] = script.suggested_title if script_exist else None
        v['versionNo'] = script.versionNo if script_exist else None
        v['domain'] = self.kwargs['domain']
        v['fid'] = self.kwargs['fid']
        v['lid'] = self.kwargs['lid']
        tutorials['tutorials'][k] = v
    return Response({ 'data': tutorials }, status=200)

  def get_script_exist(self, tid):
    script = None
    if Script.objects.filter(domain=self.kwargs['domain'],foss_id=int(self.kwargs['fid']),tutorial_id=int(tid), language_id=int(self.kwargs['lid'])).exists():
      script = Script.objects.filter(domain=self.kwargs['domain'],foss_id=int(self.kwargs['fid']),tutorial_id=tid, language_id=int(self.kwargs['lid'])).order_by('-versionNo').first()
      return True, script
    else:
      return False, script

  
class ScriptCreateAPIView(generics.ListCreateAPIView):
  permission_classes = [ScriptOwnerPermission]
  serializer_class = ScriptDetailSerializer

  def populatePrevNext(self, script):
    slides = ScriptDetail.objects.filter(script = script).order_by('order')
    i = 0
    for slide in slides:
      if slide.order != 1:
        slide.prevRow = slides[i-1].pk
      if slide.order != slides.count():
        slide.nextRow = slides[i+1].pk
      slide.save()
      i = i + 1

  def getUlData(self,data):
    data=str(data).replace("<li></li>","")
    soup=BeautifulSoup(data,'html.parser')
    if soup.find_all('ul'):
      all_data=soup.find_all('ul')
      for data in all_data:
        for p in data.find_all('p'):
          p.name='li'
          
    if soup.find_all('ol'):
      all_data=soup.find_all('ol')
      for data in all_data: 
        for p in data.find_all('p'):
          p.name='li'
    return str(soup)


  def scriptsData(self, html,script):
    soup=BeautifulSoup(html,'html.parser')
    table=soup.find("table") 
    # print(table)
    if(table.find("tbody")):
      table=table.find("tbody")
    details=[]
    count=-1
    for row in table.find_all('tr'):
      count+=1
      if row.find_all("th"):
        columns = row.find_all('th')
      elif row.find_all('td'):  
        columns = row.find_all('td')
      try:
        details.append({"order": count,"cue": self.getUlData(columns[0]),"narration": self.getUlData(columns[1]),"script":script.pk})
      except:
        continue
    details.pop(0)
    return details

  def get_queryset(self): 
    try:
      script = Script.objects.get(domain=self.kwargs['domain'], foss_id=self.kwargs['fid'], language_id=self.kwargs['lid'], tutorial_id=self.kwargs['tid'], versionNo=self.kwargs['vid'])
      user=self.request.user
      if is_DomainReviewer(self.kwargs['domain'], self.kwargs['fid'], self.kwargs['lid'],  user.username) or is_QualityReviewer(self.kwargs['domain'], self.kwargs['fid'], self.kwargs['lid'],  user.username)  or script.user == user or script.status == True:
        script_details = ScriptDetail.objects.filter(script = script)
        ordering = script.ordering

        if (len(ordering) != 0):
          ordering = ordering.split(',')
          ordering = list(map(int, ordering))
          script_details = sorted(script_details, key=lambda s: ordering.index(s.pk))
        
        return script_details
    except:
      return None

  def get(self, request, fid, tid, lid, vid, domain):
    script = Script.objects.get(domain=domain, foss_id=fid, language_id=lid, tutorial_id=tid, versionNo=vid)
    serialized = ScriptSerializer(script)
    return Response(serialized.data, status=200)

  def create(self, request, fid, tid, lid, vid, domain):
    details=[]
    create_request_type=request.data['type']
    if not Script.objects.filter(domain=domain, foss_id=int(fid), language_id=int(lid), tutorial_id=int(tid), versionNo=int(vid)).exists():
      tutorial = get_tutorial_details(domain, fid, lid, tid)
      script = Script.objects.create(
        domain = domain,
        foss = tutorial['foss'],
        foss_id = int(fid),
        language = tutorial['language'],
        language_id = int(lid),
        tutorial = tutorial['tutorial']['tutorial'],
        outline = tutorial['tutorial']['outline'],
        tutorial_id = int(tid),
        user = self.request.user, 
        versionNo=int(vid), 
        editable=True)
      if int(vid) > 1:
        prevScript = Script.objects.get(domain=domain, foss_id=int(fid), language_id=int(lid), tutorial_id=int(tid), versionNo=int(vid)-1) #Get previous version
        prevScript.editable = False
        prevScript.save()
    else:
      script = Script.objects.get(domain=domain, foss_id=int(fid), language_id=int(lid), tutorial_id=int(tid), versionNo=int(vid))

    if(create_request_type=='form'):
      details = request.data['details']
      for item in details:
        item.update( {"script":script.pk})
    elif(create_request_type=='file'):
      myfile=request.FILES['docs']
      fs = FileSystemStorage()
      uid=uuid.uuid4().hex
      filename = fs.save(uid, myfile)
      doc_file=os.getcwd()+'/media/'+filename
      #os.system('libreoffice --convert-to html '+doc_file)
      if subprocess.check_call('soffice --convert-to html '+doc_file+' --outdir media', shell=True) ==0:
        html_file= 'media/'+uid+".html"

        with open(html_file,'r') as html:
          details=self.scriptsData(html,script)
        os.system('rm '+ doc_file + ' '+html_file)
      else:
        return Response({'status': False, 'message': 'Failed to create script'},status = 500)

    elif (create_request_type=="template"):
      data=request.data['details']
      details=self.scriptsData(data,script)

    serialized  =  ScriptDetailSerializer(data  =  details,many  =  True) #inserting a details array without iterating
    if serialized.is_valid():
      serialized.save()
      if create_request_type=="file" or create_request_type=="template":
        self.populatePrevNext(script)
      
      if (create_request_type == 'form'):
        for slide in serialized.data:
          slideid = str(slide.get('id'))

        if 'creatingonline' in request.data:
          self.populatePrevNext(script)

        if 'prevSlideID' in request.data:
          prevSlideID = request.data['prevSlideID']
          newRow = ScriptDetail.objects.get(pk=int(slideid))          
          q1 = ScriptDetail.objects.get(pk=prevSlideID) #Previous row
          if q1.nextRow:
            q2 = ScriptDetail.objects.get(pk=q1.nextRow) #Next row
            q2.prevRow = newRow.pk
            newRow.nextRow = q2.pk
            q2.save()
          q1.nextRow = newRow.pk
          newRow.prevRow = q1.pk
          q1.save()
          newRow.save()

        # script.save()

      return Response({'status': True, 'data': serialized.data },status = 201)
    return Response({'status': False, 'message': 'Failed to create script'},status = 500)

  def delete(self, request, fid, tid, lid, vid, domain):
    try:
      script = Script.objects.get(domain=domain, foss_id=int(fid), language_id=int(lid), tutorial_id=int(tid), versionNo=int(vid))
      script.delete()
      return Response({'status': True},status = 202)
    except:
      return Response({'status': False, 'message': 'Failed to delete script'},status = 403)

  def patch(self, request, fid, tid, lid, vid, domain):
    try:
      script = Script.objects.get(domain=domain, foss_id=int(fid), language_id=int(lid), tutorial_id=int(tid), versionNo=int(vid))

      if 'suggested_title' in request.data:
        suggested_title = request.data['suggested_title']
        script.suggested_title = suggested_title
        script.save()
        return Response({'suggested_title': suggested_title, 'message': 'Successfully updated suggested title'}, status = 200) 

      if 'status' in request.data:
        if  not is_DomainReviewer(domain, fid, lid, request.user.username) or not is_QualityReviewer(domain, fid, lid, request.user.username):
          return Response({'message': 'You do not have review permission.'}, status = 403) 
        status = request.data['status']
        script.status = status
      
        script.published_by = request.user
        script.published_on = timezone.now()
        if status == False:
          script.published_by = None
          script.published_on = None
        script.save()
        return Response({'status': status, 'message': 'Successfully changed status of script'}, status = 200) 
    except:
      return Response({'message': 'Failed to change status'}, status = 500) 

class ScriptDetailAPIView(generics.ListAPIView):
  permission_classes = [ScriptModifyPermission]

  def patch(self, request, script_detail_id):
    try:
      script_details  =  self.request.data
      script_details['id']=int(script_detail_id)
      script  =  ScriptDetail.objects.get(pk=script_details['id'])
      serializer  =  ScriptDetailSerializer(script, data = script_details)
      if serializer.is_valid():
        serializer.save()
        return Response({'status': True},status = 200)
      return Response({'status': False, 'message': 'Failed to update row'},status = 500)       
    except:
      return Response({'status': False, 'message': 'Failed to update row'},status = 403)       

  def delete(self, request, script_detail_id):
    try:
      script_slide = ScriptDetail.objects.get(pk = int(self.kwargs['script_detail_id']))

      if script_slide.prevRow:
        q1 = ScriptDetail.objects.get(pk=script_slide.prevRow)
        q1.nextRow = script_slide.nextRow
        q1.save()

      if script_slide.nextRow:
        q2 = ScriptDetail.objects.get(pk=script_slide.nextRow)
        q2.prevRow = script_slide.prevRow
        q2.save()

      if not ScriptDetail.objects.filter(script_id = script_slide.script.pk).exists(): 
        Script.objects.delete(pk=script_slide.script.pk)

      script_slide.delete()
      return Response({'status': True},status = 202) 
    except:
      return Response({'status': False, 'message': 'Failed to delete row'},status = 403)       

class PublishedScriptAPI(APIView):
  # permission_classes = [PublishedScriptPermission]

  def get(self, request):
    scripts = Script.objects.filter(status=True)
    data = ScriptListSerializer(scripts, many=True).data
    return Response({ 'data': data }, status=200)

class ForReviewScriptAPI(APIView):
  permission_classes = [ReviewScriptPermission]

  def get(self, request):
    #Select only the latest scripts (editable=True) which are not published(status=False)
    scripts = Script.objects.filter(status=False, editable=True)
    tutorials_group = {}

    for script in scripts:
      if script.foss_id not in tutorials_group:
        tutorials_group[script.foss_id] = {
          'name': script.foss,
          'data': []
        }

      tutorials_group[script.foss_id]['data'].append(script.tutorial)

    # print(tutorials_group)
    return Response({ 'data': tutorials_group })

class RelativeOrderingAPI(generics.ListAPIView):
  permission_classes = [ScriptOwnerPermission]

  def patch(self, request, script_id):
    move = request.data['move']
    slideid = request.data['slideid']
    if move == -1: # Move up
      q1 = ScriptDetail.objects.get(pk=slideid)     # Current
      q2 = ScriptDetail.objects.get(pk=q1.prevRow)  # Previous

      if q1.nextRow:
        q3 = ScriptDetail.objects.get(pk=q1.nextRow)  # Next
        q2.nextRow = q3.pk
        q3.prevRow = q2.pk
        q3.save()
      else:
        q2.nextRow = None

      if q2.prevRow:
        q4 = ScriptDetail.objects.get(pk=q2.prevRow)  # Previous previous
        q1.prevRow = q4.pk
        q4.nextRow = q1.pk
        q4.save()
      else:
        q1.prevRow = None

      q1.nextRow = q2.pk
      q2.prevRow = q1.pk
      q1.save()
      q2.save()

    if move == 1: # Move down
      q1 = ScriptDetail.objects.get(pk=slideid)     # Current
      q2 = ScriptDetail.objects.get(pk=q1.nextRow)  # Next

      if q1.prevRow:
        q3 = ScriptDetail.objects.get(pk=q1.prevRow)     # Previous
        q2.prevRow = q3.pk
        q3.nextRow = q2.pk
        q3.save()
      else:
        q2.prevRow = None

      if q2.nextRow:
        q4 = ScriptDetail.objects.get(pk=q2.nextRow)  # Next next
        q1.nextRow = q4.pk
        q4.prevRow = q1.pk
        q4.save()
      else:
        q1.nextRow = None

      q1.prevRow = q2.pk
      q2.nextRow = q1.pk
      q1.save()
      q2.save()

    return Response({ 'status': True }, status=200)

class CommentCreateAPIView(generics.ListCreateAPIView):
  serializer_class=CommentSerializer
  permission_classes = [CanCommentPermission]

  def get_queryset(self):
    try:
      script_detail=ScriptDetail.objects.get(pk=int(self.kwargs['script_detail_id']))
      return Comment.objects.filter(script_details = script_detail).order_by('created')
    except:
      return None

  def create(self,request,script_detail_id):
    try:
      script_data=ScriptDetail.objects.get(pk=script_detail_id)
      self.check_object_permissions(request, script_data)
      if script_data.comment_status == False:
        script_data.comment_status=True
        script_data.save()
      Comment.objects.create(comment=request.data['comment'],user=self.request.user,script_details=script_data)
      return Response({'status': True},status = 202)
    except:
      return Response({'status': False, 'message': 'Not allowed to comment'},status = 500)       

class CommentAPI(generics.ListAPIView):
  permission_classes = [CommentOwnerPermission]

  def patch(self, request, comment_id):
    try:
      comment = Comment.objects.get(id=comment_id)
      self.check_object_permissions(request, comment)
      serializer = CommentSerializer(comment, request.data, partial=True)
      if (serializer.is_valid()):
        serializer.save()
        return Response({'message': 'Updated the comment', 'data': serializer.data})
    except:
      return Response({'message': 'Unauthorized request to update comment'}, status=500)

  def delete(self, request, comment_id):
    try:
      comment = Comment.objects.get(id=comment_id)
      self.check_object_permissions(request, comment)
      script = comment.script_details
      comment.delete()

      script.comment_status = len(Comment.objects.filter(script_details=script)) > 0
      script.save()
      return Response({'status': True}, status=200)
    except:
      return Response({'message': 'Unauthorized request to update comment'}, status=403)

class ReversionListView(generics.ListAPIView):
  serializer_class = ReversionSerializer
  permission_classes = [IsAuthenticatedOrReadOnly]

  def get_queryset(self):
    try:
      script_detail=ScriptDetail.objects.get(pk=int(self.kwargs['script_detail_id']))
      reversion_data = Version.objects.get_for_object(script_detail)
      data = []
      count=0
      for i in reversion_data:
        count+=1
        result=i.field_dict
        rev_time=i.revision.date_created+timedelta(hours=5,minutes=30)
        result.update({"reversion_id": count,"date_time":rev_time.strftime("%Y-%m-%d %I:%M %p"),"user":i.revision.user})
        data.append(result)
      return ReversionSerializer(data,many=True).data
    except:
      return None

class ReversionRevertView(generics.CreateAPIView):
  permission_classes = [CanRevisePermission]

  def patch(self,request,script_detail_id,reversion_id):
    try:
      script_detail=ScriptDetail.objects.get(pk=int(self.kwargs['script_detail_id']))
      self.check_object_permissions(request, script_detail)
      reversion_data = Version.objects.get_for_object(script_detail)
      reversion_data[int(self.kwargs['reversion_id'])-1].revision.revert()
      return Response({'status': True},status = 201)
    except:
      return Response({'status': False, 'message': 'Failed'},status = 403)
