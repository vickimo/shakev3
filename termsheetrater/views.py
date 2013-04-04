from django.shortcuts import render_to_response
from termsheetrater.forms import TermForm, SimpleFileForm
from django.template import RequestContext
from termsheetrater.models import TermFields, TermChoices
from django.http import HttpResponseRedirect, HttpResponse
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.plaintext.writer import PlaintextWriter
from django.views.decorators.csrf import csrf_exempt
from subprocess import call
from django.utils import simplejson
# realpath() with make your script run, even if you symlink it :)
# cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
# if cmd_folder not in sys.path:
# 	sys.path.insert(0, cmd_folder)

# # use this if you want to include modules from a subforder
# cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"subfolder")))
# if cmd_subfolder not in sys.path:
# 	sys.path.insert(0, cmd_subfolder)

def pdf_to_txt(path):

    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

    fp = file(path, 'rb')
    process_pdf(rsrcmgr, device, fp)
    fp.close()
    device.close()

    str = retstr.getvalue()
    retstr.close()
    if len(str) < 10:
		jpgfp = path[:len(path)-3] + 'jpg'
		pdf_to_jpg(path,jpgfp)
		return ocr_image(path[:len(path)-4], '.jpg')
    else:
    	return str

def pdf_to_jpg(pdfpath,jpgpath):
	gmcall = "gm convert -append -type grayscale -density 300 " + pdfpath + " " + jpgpath
	call([gmcall], shell=True)

def ocr_image(filename, extension):
	imagepath = filename + extension
	txtpath = filename + '.txt'
	tesscall = 'tesseract ' + imagepath + ' ' + filename
	call([tesscall], shell=True)
	return open(txtpath, 'rb').read()	

@csrf_exempt
def upload(request):
	#connection._rollback()
	if request.FILES:
		if 'file' in request.FILES:
			result = ''
			f = request.FILES['file']
			fp = 'shake_v3/static/data/' + str(f)
			fp2 = fp[:len(fp)-3] + 'txt'
			if fp[len(fp)-3:len(fp)] == 'pdf':
				with open(fp, 'wb+') as pdff:
					for chunk in f.chunks():
						pdff.write(chunk)
				result = pdf_to_txt(fp)
				with open(fp2, 'wb+') as txtf:
					txtf.write(result)			
			elif fp[len(fp)-3:len(fp)] == 'rtf':
				with open(fp, 'wb+') as rtff:
					for line in f:
						rtff.write(line)
				doc = Rtf15Reader.read(open(fp, 'rb'))
				doctxt = PlaintextWriter.write(doc).getvalue()
				with open(fp2, 'wb+') as txtf:
					for line in doctxt:
						txtf.write(line)
				f = str(f)[:-4] + ".txt"
				result = doctxt
			else:
				with open(fp2, 'wb+') as txtf:
					for line in f:
						txtf.write(line)
				result = open(fp2, 'r').read()
		response_dict = generate_term_dict(result)
		response_dict['fp'] = 'static/data/' + str(f)
		# with txt search for terms, if found that term is good.
		#response_dict = {"liq pref, seniority": "senior"}
		return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
	elif request.POST:
		rating = ""
		score = custom_POST_to_score(request)
		if score > 4.5:
			rating = 'A+'
		elif score > 4:
			rating = 'A'
		elif score > 3.5:
			rating = 'B+'
		elif score > 3:
			rating = 'B'
		elif score > 2.5:
			rating = 'C+'
		elif score > 2:
			rating = 'C'
		elif score > 1:
			rating = 'D'
		else:
			rating = 'F'
		return HttpResponse(rating)
		#return render_to_response('upload.html', {'score': score, 'terms': TermFields.objects.all().order_by('term'), 'choices': TermChoices.objects.all().order_by('choice_label')}, context_instance = RequestContext(request))
	else:
		score = 0
		return render_to_response('upload.html', {'score': score, 'terms': TermFields.objects.all().order_by('term'), 'choices': TermChoices.objects.all().order_by('choice_label')}, context_instance = RequestContext(request))

def generate_term_dict(text):
	text = text.lower()
	text1 = text.replace(',','').replace(' ','')
	termdict = {}
	# pre-money price more > 60% of pre+post better
	if (text.find('valuation of the company') > -1) and (text.find('amount of the offering') > -1):
		a = text1.find('amountoftheoffering')
		termdict['amount of the offering'] = filter(str.isdigit, text1[a:a+40])
		b = text1.find('valuationofthecompany')
		termdict['pre-money valuation'] = filter(str.isdigit, text1[b:b+40])

	if (text.find('anti-dilution') > -1) or (text.find('antidilution') > -1) or (text.find('anti dilution') > -1):
		if text.find('broad-based') > -1:
			termdict['anti-dilution, base'] = 'broad'
			termdict['anti-dilution'] = 'average'
		elif text.find('narrow-based') > -1:
			termdict['anti-dilution, base'] = 'narrow'
			termdict['anti-dilution'] = 'average'
		elif text.find('full-ratchet') > -1:
			termdict['anti-dilution'] = 'ratchet'

	if text.find('pay-to-play') > -1:
		termdict['pay-to-play'] = 'yes'
	else:
		termdict['pay-to-play'] = 'no'

	if text.find('voting for directors') > -1:
		p = 'preferredwillbeentitledtoelect'
		c = 'commonstockwillbeentitledtoelect'
		a = text1.find(p)
		a1 = text1[a:].find('directors')
		b = text1.find(c)
		b1 = text1[b:].find('directors')
		termdict['preferred directors'] = text2int(text1[a+len(p):a+a1])
		termdict['common directors'] = text2int(text1[b+len(c):b+b1])

	if text.find('pari passu') > -1:
		termdict['liq pref, seniority'] = 'pari passu'
	elif text.find('senior to common') > -1:
		termdict['liq pref, seniority'] = 'senior'
		if text.find('participates in liquidation proceeds') > -1:
			termdict['liq pref, participating'] = 'yes'
		elif text.find('does not participate in further liquidation proceeds') > -1:
			termdict['liq pref, participating'] = 'no'
		if text.find('cap on participation at') > -1:
			termdict['liq pref, capped'] = 'yes'
		elif text.find('no cap on participation') > -1:
			termdict['liq pref, capped'] = 'no'
	if text.find('original purchase price') > -1:
		termdict['liq pref, amount'] = 'original purchase price'
	elif text.find('times the original purchase price') > -1:
		a = text.find('amount:')
		b = text.find('times the original purchase price')
		termdict['liq pref, amount multiple'] = text[a+8:b]
		termdict['liq pref, amount'] = 'X times the original purchase price'
	print termdict
	return termdict

def reset_tables(request):
	#connection._rollback()
	term_deets = {
		"pre-money valuation": {},
		"amount of the offering": {},
		"price": {'0-0.6':1, '0.6-0.65':1.5, '0.65-0.7':2, '0.7-0.75':2.5, '0.75-0.8':3, '0.8-0.85':3.5, '0.85-0.9':4, '0.9-0.95':4.5, '0.95-1':5}, 
		"liq pref, seniority": {"senior":3, "pari passu":5}, #"liq pref, seniority": {"senior":3, "pari passu":4, "junior":5}, 
		"liq pref, amount": {"original purchase price":3,"X times the original purchase price":1},
		"liq pref, participating": {"yes":1, "no":5}, 
		"liq pref, capped": {"yes":3, "no":1}, 
		"pay-to-play": {"yes":4, "no":3},
		"employee pool": {"0-5%":3, "5-15%":5, "15-20%":3, ">20%":1},
		"anti-dilution": {"average":5, "ratchet":1},
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
	terms_shown = ['liq pref, seniority', 'liq pref, participating',]
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

def term_dict_to_score(term_dict):
	score = 0
	total_weight = 0
	for k,v in term_dict.iteritems():
		term_field = TermFields.objects.get(term__iexact = k)
		term_choice = TermChoices.objects.filter(term_field = term_field, choice_label__iexact = v)[0]
		weight = term_field.weight
		value = term_choice.value
		score = score + weight*value
		total_weight = total_weight + weight
	return str("{0:.2f}".format(score/total_weight)) + ('/5')

def POST_to_score(request):
	term_score = 1
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
		term_score = term_dict_to_score(term_dict)
	return term_score

def custom_POST_to_score(request):
	term_score = 0.0
	total_weight = 0.0
	r = request.POST
	if len(r["pre-money valuation"]) > 0 and len(r["amount of the offering"]) > 0:
		total_weight = total_weight + 1
		pre_money = float(r["pre-money valuation"])
		post_money = pre_money + float(r["amount of the offering"])
		if pre_money < 0.6*post_money:
			term_score = term_score + 1
		elif pre_money < 0.65*post_money:
			term_score = term_score + 1.5
		elif pre_money < 0.7*post_money:
			term_score = term_score + 2
		elif pre_money < 0.75*post_money:
			term_score = term_score + 2.5
		elif pre_money < 0.8*post_money:
			term_score = term_score + 3
		elif pre_money < 0.85*post_money:
			term_score = term_score + 3.5
		elif pre_money < 0.9*post_money:
			term_score = term_score + 4
		elif pre_money < 0.95*post_money:
			term_score = term_score + 4
		else: #tiny
			term_score = term_score + 5
	if "anti-dilution" in r:
		total_weight = total_weight + 1
		if r["anti-dilution"] == "average":
			if "anti-dilution, base" in r and r["anti-dilution, base"] == "narrow":
				term_score = term_score + 3
			elif "anti-dilution, base" in r and r["anti-dilution, base"] == "broad":
				term_score = term_score + 5
			else: #not defined
				term_score = term_score + 4
		elif r["anti-dilution"] == "ratchet":
			term_score = term_score + 1
	if "pay-to-play" in r:
		total_weight = total_weight + 1
		if r['pay-to-play'] == 'yes':
			term_score = term_score + 5
		else: #not pay-to-play
			term_score = term_score + 3
	if len(r['preferred directors']) > 0 and 'common directors' in r:
		total_weight = total_weight + 1
		p = int(r['preferred directors'])
		c = int(r['common directors'])
		if p > c:
			term_score = term_score + 1
		elif p < c:
			term_score = term_score + 5
		else: #equal
			term_score = term_score + 3
	if 'liq pref, seniority' in r:
		total_weight = total_weight + 1
		liqscore = 0
		if r['liq pref, seniority'] == 'senior':
			if 'liq pref, participating' in r > 0:
				if r['liq pref, participating'] == 'yes':
					if 'liq pref, capped' in r:
						if r['liq pref, capped'] == 'yes':
							liqscore = 2
						else: # not capped
							liqscore = 1
					else: # capped not chosen
						liqscore = 1.5
				else: # not participating
					liqscore = 3
			else:
				liqscore = 3
			if 'liq pref, amount' in r and r['liq pref, amount'] != 'original purchase price' and len(r['liq pref, amount multiple']) > 0:
				if int(r['liq pref, amount multiple']) > 1 and int(r['liq pref, amount multiple']) < 2 and liqscore >= 1.5:
					liqscore = liqscore - 1.5
				elif int(r['liq pref, amount multiple']) >= 2 and liqscore >= 3:
					liqscore = liqscore - 3
		else: #pari passu
			liqscore = 5
		term_score = term_score + liqscore
	if total_weight is 0.0:
		return 0
	return term_score/total_weight

def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

def index(request):
	#connection._rollback()
	term_score = 0
	if request.POST:
		term_score = POST_to_score(request)
	return render_to_response('index.html', {'score': term_score, 'selected': {"liq pref, seniority": "senior"}, 'terms': TermFields.objects.all().order_by('term'), 'choices': TermChoices.objects.all().order_by('choice_label')}, context_instance = RequestContext(request))

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