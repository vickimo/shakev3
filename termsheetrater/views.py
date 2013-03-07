from django.shortcuts import render_to_response
from termsheetrater.forms import TermForm, SimpleFileForm
from django.template import RequestContext
from termsheetrater.models import TermFields, TermChoices
from django.http import HttpResponseRedirect
from django.db import connection

def upload(request):
	connection._rollback()
	term_score = 0
	choices = {}
	if request.POST:
		if 'file' in request.FILES:
			f = request.FILES['file']
			filepath = 'data/' + str(f)
			with open(filepath	, 'wb+') as destination:
				for chunk in f.chunks():
					destination.write(chunk)
			doc = PdfFileReader(file(filepath, "rb"))
# check type, if pdf, convert to txt, if docx convert to txt
# with txt search for terms, if found that term is good.
			return http.HttpResponseRedirect(' upload_success.html')
		#return render_to_response('index.html', {'score': term_score, 'terms': TermFields.objects.all().order_by('term'), 'choices': choices}, context_instance = RequestContext(request))
	else:
		form = SimpleFileForm()
		return render_to_response('upload.html', { 'form': form }, context_instance = RequestContext(request))

def reset_tables(request):
	connection._rollback()
	term_deets = {
		"price": {}, 
		"liq pref, seniority": {"senior":3, "pari passu":4, "junior":5}, 
		"liq pref, participating": {"yes":1, "no":5}, 
		"liq pref, multiple": {"1":5,"2":4,"3":3,"4":2,"5":1},
		"pay-to-play": {"yes":4, "no":3},
		"employee pool": {"0-5%":3, "5-15%":5, "15-20%":3, ">20%":1},
		"anti-dilution": {"average":5, "rachet":1},
		"anti-dilution, base": {"narrow":1, "broad":5},
		"board, number": {"1-2":3,"3-8":5,"9-11":3},
		"board, election": {"investors":1, "split":3, "founders":5},
		"prot prov, change in terms of equity series": {"no":1, "yes":5},
		"prot prov, authorize more stock": {"no":1, "yes":5},
		"prot prov, issue senior stock": {"no":1, "yes":5},
		"prot prov, buy back common": {"no":1, "yes":5},
		"prot prov, sell the company": {"no":1, "yes":5},
		"prot prov, change the cert or bylaws": {"no":1, "yes":5},
		"prot prov, change the size of the board": {"no":1, "yes":5},
		"prot prov, pay/Declare a dividend": {"no":1, "yes":5},
		"prot prov, borrow money": {"no":1, "yes":5},
		"drag along": {"yes":1, "no":5}, 
		"conversion, automatic": {"no":1, "yes":5},
		"conversion, voluntary": {"no":1, "yes":5},
		"conversion, ratio": {">1:1":1, "1:1":5},
		"dividends, % of equity": {"12-15%":1, "9-11%":2, "5-9%":3, "1-4%":4, "0%":5},
		"redemption rights": {"mandatory":1, "investor option":3, "none":5},
		"registration rights, demand": {"yes":3, "no":5},
		"registration rights, piggyback": {"yes":3, "no":5},
		"registration rights, S-3": {"yes":3, "no":5},
		"right of first refusal": {"yes":3, "no":5},
		"voting rights, multiple of common stock voting": {">1:1":1, "1:1":5},
		"co-sale agreement": {"yes":3, "no":5},
		"vesting": {"5 years":1, "4 years":2, "3 years":3, "1-2 years":4, "0 years":5}
	}
	for term, choices in term_deets.iteritems():
		try:
			term_field = TermFields.objects.get(term__iexact = term)
			term_field.weight = 1.0
			term_field.save()
		except:
			term_field = TermFields.objects.create(term = term, weight = 1.0)
			term_field.save()
		for key, value in choices.iteritems():
			term_field = TermFields.objects.get(term__iexact = term)
			term_choice = TermChoices.objects.filter(term_field = term_field, choice_label__iexact = key)
			if len(term_choice) == 0:
				term_choice = TermChoices.objects.create(term_field = term_field, choice_label = key, value = value)
			else:
				term_choice = TermChoices.objects.get(term_field = term_field, choice_label = key)
				term_choice.value = value
			term_choice.save()
	return HttpResponseRedirect('/termsheet/')

def update_term(term, choice, value, weight):
	try:
		term_field = TermFields.objects.get(term__iexact = term)
		term_field.weight = weight
		term_field = TermFields.objects.get(term__iexact = term)
		term_choice = TermChoices.objects.filter(term_field = term_field, choice_label__iexact = key)[0]
		term_choice.value = value
	except:
		return -1

def generate_score(term_dict):
	score = 0
	total_weight = 0
	for k,v in term_dict.iteritems():
		term_field = TermFields.objects.get(term__iexact = k)
		term_choice = TermChoices.objects.filter(term_field = term_field, choice_label__iexact = v)[0]
		weight = term_field.weight
		value = term_choice.value
		score = score + weight*value
		total_weight = total_weight + weight
	return score/total_weight


def index(request):
	connection._rollback()
	term_score = 0
	if request.POST:
		term_dict = {}
		for k,v in request.POST.iteritems():
			user_input = k.split("+")
			if user_input[0] == "weight" and v:
				term = user_input[1]
				term_field = TermFields.objects.get(term__iexact = term)
				term_field.weight = v
				term_field.save()
			if user_input[0] == "term" and v:
				term_dict[user_input[1]] = v
			if user_input[0] == "value" and v:
				term = user_input[1]
				choice = user_input[2]
				term_field = TermFields.objects.get(term__iexact = term)
				term_choice = TermChoices.objects.filter(term_field = term_field, choice_label__iexact = choice)[0]
				term_choice.value = v
				term_choice.save()
		if len(term_dict) > 0:
			term_score = generate_score(term_dict)
	return render_to_response('index.html', {'score': term_score, 'terms': TermFields.objects.all().order_by('term'), 'choices': TermChoices.objects.all().order_by('choice_label')}, context_instance = RequestContext(request))

def result(request):
	if request.method == 'POST':
		form = TermForm(data=request.POST)
		if form.is_valid():
			kwargs = form.cleaned_data
			employeepool = kwargs['employeepool']
			rating = rate_employee_pool(employeepool)
			return render_to_response('result.html', {'result': rating})
	form = TermForm
	return render_to_response('index.html', {'form': form}, context_instance = RequestContext(request))