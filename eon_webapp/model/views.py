from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy,reverse
from django.views import generic
from django.shortcuts import redirect
from django.views.generic.edit import CreateView,UpdateView,DeleteView,FormView
from .forms import ModelViewForm,GraphSpecifyForm
from .models import UserModel
from .models import User
from forum.models import Thread, Forum, Comment
from forum.forms import CommentCreationForm

import os
import zipfile
import random
import subprocess
import json
import pandas as pd

"""
TODO:
Make graph page refresh graph only (send data via js request?)
Allow user to input paramters in a field for each parameter
Clean up interfaces
Add group permissions

"""

CODE_REPOSITORIES_PATH="/home/joe/EON/eon_webapp/model_code"

class Index(generic.ListView):
    #UserModel.objects.get(author_PK=User.pk)
    if(True):
        model = UserModel
        template_name = "model/index.html"
        context_object_name = "UserModels" #use this in the template
        fields = []
    def get_queryset(self):
        return UserModel.objects.all()

    #def detail(request,):

class CreateUserModel(CreateView):
    model = UserModel
    fields = ['model_name','description','code_language','executable_file_name']
    template_name = 'model/UserModel_Create.html'
    def get_success_url(self):
        return reverse('view_user_model', args=(self.object.id,))
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["text_fields"]=['model_name','description','executable_file_name']
        data["languages"]=['C','Python']
        data["dropdown_fields"]=["code_language"]
        return data
    def form_valid(self, form):
        user_model = form.save(commit=False)
        user_model.owner = self.request.user
        user_model.thread = Thread.objects.create(
        thread_name=user_model.model_name,
        poster=self.request.user,
        description="Auto generated first post for model: %s"%user_model.model_name,
        forum=Forum.objects.get(pk=1),
        )
        # TODO: ensure that folder location doesnt clash! usually not an issue but COULD happen
        model_folder_location = CODE_REPOSITORIES_PATH+"/"+str(user_model.owner) + "_"+str(random.randint(0,999999))
        user_model.folder_location=model_folder_location
        # Create folder for user code, then copy the file from memory to folder
        os.mkdir(model_folder_location)
        specs_json = self.request.FILES["specs_json"]
        with open(model_folder_location+"/specification.json", 'wb+') as destination:
            for chunk in specs_json.chunks():
                destination.write(chunk)
        user_code = self.request.FILES["model_code"]
        with open(model_folder_location+"/zipped_code.zip", 'wb+') as destination:
            for chunk in user_code.chunks():
                destination.write(chunk)
        # unzip the files in place
        with zipfile.ZipFile(model_folder_location+"/zipped_code.zip", 'r') as zipped_code:
            zipped_code.extractall(model_folder_location)
        os.remove(model_folder_location+"/zipped_code.zip") #zip not needed after extraction
        return super(CreateUserModel, self).form_valid(form)

    #context_object_name = "UserModel"


# TODO: REMOVE ONCE IT IS COMPLETELY DEPRECATED
# class GraphSpecifyDetailedUserModel(generic.DetailView):
#     model = UserModel
#     context_object_name = "UserModel" #use this in the template
#     template_name = 'model/Display_UserModel.html'
#     def get_queryset(self):
#         return UserModel.objects.all()
#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         data["url_path"] = "/model/UpdateGraphJson/"+str(data["UserModel"].id)
#         data["owner_name"] = User.objects.get(pk=data["UserModel"].owner_id).username
#         data['form']=GraphSpecifyForm(data["UserModel"])
#         # TODO: CHANGE THIS TO LOGGING
#         # runs the code in firejail within the directory
#         print("RUNNING CODE")
#         if os.path.exists(data["UserModel"].folder_location+"/output.csv"):
#             os.remove(data["UserModel"].folder_location+"/output.csv")
#         json_location = "%s/specification.json"%folder_location
#         with open(json_location, 'r') as json_f:
#             specification_dict = json.load(json_f)
#         default_params=[param for param,key in enumerate(specification_dict["parameter_defaults"])]
#         run_command=["firejail","--private="+data["UserModel"].folder_location,"./"+data["UserModel"].executable_file_name]
#         run_command+=params
#         subprocess.run(run_command)
#         # output is now in output.csv (should be anyway...)
#         # TODO: catch error if output.csv doesn't exist
#         with open(data["UserModel"].folder_location+"/output.csv") as output_file:
#             output = output_file.readlines()
#         output = [x.strip() for x in output]
#         header = output[0].split(",")
#         # data_dict = {}
#         # for head in header:
#         #     data_dict[head]=[]
#         # for line in output[1:]:
#         #     line_contents=line.split(",")
#         #     for index,head in enumerate(header):
#         #         data_dict[head].append(line_contents[index])
#         # data["col1"]=data_dict[header[0]]
#         # data["col2"]=data_dict[header[1]]
#         data["output"]=output
#         return data

class GraphSpecifyFormView(FormView):
    form_class=GraphSpecifyForm
    success_url=reverse_lazy('model_index')
    template_name='home.html'

class UpdateUserModel(UpdateView):
    context = {}
    context["ModelViewForm"] = ModelViewForm()
    model = UserModel

    fields = ['model_name','description','executable_file_name']
    template_name = 'model/Update_UserModel.html'


class UserModelDelete(DeleteView):
    model = UserModel
    context_object_name = "UserModel" #use this in the template
    success_url = reverse_lazy('model_index')
    template_name = 'model/UserModel_confirm_delete.html'



    #context_object_name = "UserModel"
class CreateModelView(UpdateView):
    fields = ['model_name','description','EONid','uploaded_code']
    template_name = 'model/Update_UserModel.html'
    print(UserModel.model_name)


    success_url = ('Display-UserModel')
    template_name = 'ModelView_form.html'

    def get_queryset(self):
        return UserModel.objects.all()

class UpdateModelView(UpdateView):
    model = UserModel
    fields = ['model_name','description','EONid','uploaded_code']

    #context_object_name = "UserModel"
    template_name = 'model/Update_UserModel.html'
    print(UserModel.model_name)


    success_url = ('Display-UserModel')
    template_name = 'ModelView_form.html'

    def get_queryset(self):
        return UserModel.objects.all()

def update_graph_json(request,model_id):
    if request.method == 'POST':
        input_field_list = str(request.body.decode("utf-8")).split('&')[1:]
        json_dict = {}
        json_dict["parameter_bounds"]={}
        json_dict["graphs"]={}
        for index,input_field in enumerate(input_field_list):
            field,input=input_field.split("=")
            if "param" in field:
                json_dict["parameter_bounds"][field]=input
            if "graph_title" in field:
                x_axis=input_field_list[index+1].split("=")[1]
                y_axis=input_field_list[index+2].split("=")[1]
                json_dict["graphs"]["graph"]={"x_axis":x_axis,"y_axis":y_axis,"name":input}
        model=UserModel.objects.get(pk=model_id)
        with open('%s/specification.json'%str(model.folder_location), 'w+') as fp:
            json.dump(json_dict, fp)
        print(model.folder_location)
    return redirect("view_user_model",pk=model_id)

def view_user_model(request,pk):
    model = UserModel.objects.get(pk=pk)
    context={"id":pk,"url_path":"/model/View/%i/"%pk}
    context["thread"]=model.thread
    context["comments"]=Comment.objects.filter(thread = model.thread)

    folder_location = str(model.folder_location)
    csv_location = "%s/output.csv"%folder_location
    json_location = "%s/specification.json"%folder_location
    with open(json_location, 'r') as json_f:
        specification_dict = json.load(json_f)
    params_list=specification_dict["parameters"]
    default_params=[param["default"] for param in params_list]
    run_command = []
    if int(model.code_language) == 0:
        run_command = ["firejail","--private="+model.folder_location,"./"+model.executable_file_name]
    elif int(model.code_language) == 2:
        run_command = ["Rscript", model.executable_file_name]
    if request.method=='POST':
        params_changed=str(request.body.decode("utf-8")).split('&')[1:]
        params_for_code_list=[]
        for index,param in enumerate(default_params):
            for param_changed in params_changed:
                if str(index) in param_changed.split("=")[0]:
                    param = param_changed.split("=")[1]
            params_for_code_list.append(param)
        if os.path.exists(model.folder_location+"/output.csv"):
            os.remove(model.folder_location+"/output.csv")
        run_command+=params_for_code_list
        subprocess.run(run_command,cwd=model.folder_location)
    else:
        if os.path.exists(model.folder_location+"/output.csv"):
            os.remove(model.folder_location+"/output.csv")
        run_command+=default_params
        print(run_command)
        print(model.folder_location)
        subprocess.run(run_command,cwd=model.folder_location)
    folder_location = str(model.folder_location)
    # with open(csv_location, 'r') as csv_f:
    df = pd.read_csv(csv_location)
    df.rename(inplace=True,columns=lambda x: x.strip())
    x_axis_name=specification_dict["graphs"]["graph"]["x_axis"]
    y_axis_name=specification_dict["graphs"]["graph"]["y_axis"]
    context["x_axis_name"]=x_axis_name
    context["y_axis_name"]=y_axis_name
    context["graph_name"]=specification_dict["graphs"]["graph"]["name"].replace("+"," ")
    columns=[]
    for index,row in df.iterrows():
        columns.append([row[x_axis_name],row[y_axis_name]])
    context["columns"]=columns
    parameters=[]
    for index,parameter in enumerate(default_params):
        param_dict = specification_dict["parameters"][index]
        upper_bound=param_dict["u_bound"]
        lower_bound=param_dict["l_bound"]
        if upper_bound!=lower_bound:
            parameters.append({"name":param_dict["name"],"default":parameter,
            "upper_bound":upper_bound,
            "lower_bound":lower_bound,
            "step":(float(upper_bound)-float(lower_bound))/10000,})
    context["parameters"]=parameters
    print(parameters)
    return render(request, 'model/view_user_model.html',context)

def CreateModelViewForm(request):
    form = ModelViewForm()
    if request.method == 'POST':
        print("Post")
        #form = ModelViewForm(request.POST, request.FILES)
        return render(request, 'model/Display_UserModelView.html', {'form': form})
    else:
        return render(request, 'model/Display_UserModelView.html', {'form': form})


class UpdateModelViewForm(UpdateView):
    def UpdateModelViewForm(self):
        return











#
