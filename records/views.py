from django.shortcuts import render, redirect
from .forms import DocumentForm
from .models import Thing, Item, Document, Previous_date
import csv
import os
import pandas as pd
from django.contrib import messages
from django.views.generic import TemplateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.core import validators
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q

# Upload view
@csrf_exempt
def upload (request):
    try:
        last = Item.objects.latest('modified')
        print(last)
        prev_date = Previous_date.objects.create(prev_modified=last.modified)
        prev_date.save()
    except ObjectDoesNotExist:
        last = None

    if request.method == "POST":
        form = DocumentForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            form = DocumentForm()
            obj = Document.objects.get(activated=False)
            with open(obj.document.path, 'r') as f:
                input_df = pd.read_csv(f, sep = "\t", header = 0)
                for i in range(0,len(input_df.to_dict('records'))):
                    row_dict = input_df.to_dict('records')[i]
                    try:
                        ## TODO: if the code in csv is repeating then update the code record
                        model1, create = Thing.objects.update_or_create(
                            code =row_dict["code"],
                            # description = row_dict["description"],
                            # date = row_dict["date"], 
                            # stat_one = row_dict["stat_one"], 
                            # stat_two = row_dict["stat_two"])
                            defaults = {
                            'description' : row_dict["description"],
                            'date' : row_dict["date"],
                            'stat_one' : row_dict["stat_one"],
                            'stat_two' : row_dict["stat_two"]
                            })
                        # model2 = Item.objects.create(
                        #         thing = model1, 
                        #         name = row_dict["name"], 
                        #         rating = row_dict["rating"], 
                        #         score = row_dict["score"])
                        #         # defaults = {
                        #         # 'name' : row_dict["name"],
                        #         # 'rating' : row_dict["rating"],
                        #         # 'score' : row_dict["score"]
                        #         # })
                        model2, create= Item.objects.get_or_create(
                                thing_id = model1.code,
                                # thing = model1, 
                                name = row_dict["name"], 
                                rating = row_dict["rating"], 
                                score = row_dict["score"])
                                # defaults = {
                                # 'name' : row_dict["name"],
                                # 'rating' : row_dict["rating"],
                                # 'score' : row_dict["score"]
                                # })
                        if create:
                            print("model 1 object is created.")
                            model2, create= Item.objects.get_or_create(
                                thing = model1, 
                                name = row_dict["name"], 
                                rating = row_dict["rating"], 
                                score = row_dict["score"])
                    # Collecting Validation errors
                    except ValidationError as e:
                        messages.error(request,str(e))
                obj.activated=True
                obj.save()
            messages.success(request,"Created and Updated records in two simple tables, one for each model",fail_silently=True)
        else:
            messages.warning(request, 'Please retry uploading...',fail_silently=True)
            
    else:
        form = DocumentForm()
    return render(request, 'records/upload.html', {'form': form})


# List view
class Updated_New_View(TemplateView):
    template_name = "records/list.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        list_data = []
        count = 0
        try:
            prev_date = Previous_date.objects.latest('prev_modified')
            print(prev_date.prev_modified)  
            get_prev = prev_date.prev_modified
            things = Thing.objects.filter(Q(modified__gte=get_prev) | Q(created__gte=get_prev))
            for thing in things:
                items = Item.objects.filter(Q(created__gte=get_prev) | Q(modified__gte=get_prev))
                # .exclude(created__lte=get_prev)
                for item in items:
                    data = {"code": thing.code, "description": thing.description, "date": thing.date, "stat_one": thing.stat_one, "stat_two":thing.stat_two, "name": item.name, "rating": item.rating, "score": item.score, "created": item.created,"modified":thing.modified}
                    list_data.append(data)
                    count += 1
        except ObjectDoesNotExist:
            things = Thing.objects.all()
            if things:
                for thing in things:
                    items = Item.objects.filter(thing_id=thing)
                    if items:
                        for item in items:
                            data = {"code": thing.code, "description": thing.description, "date": thing.date, "stat_one": thing.stat_one, "stat_two":thing.stat_two, "name": item.name, "rating": item.rating, "score": item.score, "created": item.created,"modified":thing.modified}
                            list_data.append(data)
                            count += 1
            else:
                None
        list_data_count = count
        context.update({
            'list_data': list_data,
            'list_data_count': int(list_data_count),
        })
        return context
    
# Delete view
def Delete_all(request):
    doc_delete = Document.objects.all().delete()
    delete_thing = Thing.objects.all().delete()
    delete_prev = Previous_date.objects.all().delete()
    return redirect('/')