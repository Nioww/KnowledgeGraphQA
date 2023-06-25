from django.shortcuts import render
from .models import Cal
from entity_get import EntityObtainer
from candidate_scoring import candi_scoring
import candidate_get

# initiate
entity_obtainer = EntityObtainer()
scorer = candi_scoring()


def qa(request):
    count = Cal.objects.count()

    if count != 0:
        ques = request.POST['ques']
        input_question = ques
        entities = entity_obtainer.mention_get(input_question)
        candidates = []
        for entity in entities:
            candidates += candidate_get.GetPaths(entity)
        if candidates == []:
            ans = '暂时没有习得相关知识。'
        else:
            the_path, the_score, mark = scorer.scoring(input_question, candidates)
            print('查询路径:', the_path, mark)
            answer = candidate_get.get_answer(the_path, mark)
            if the_score > 0.45:
                print('答案:', answer, '\n得分:', str(the_score))
                ans = answer
            else:
                ans = '或许换个问法会有答案？'
    else:
        ques = '..'
        ans = '欢迎使用计算机网络问答系统。'

    Cal.objects.create(question=ques, answer=ans, count=1)
    record = Cal.objects.all()
    return render(request, 'QAbot.html', context={'data': record})
