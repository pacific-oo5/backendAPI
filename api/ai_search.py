import re
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def get_similar_vacancies(current_vacancy, all_vacancies, top_n=6):
    current_words = set(re.findall(r'\w+', current_vacancy.name.lower()))
    similar = []

    for vacancy in all_vacancies:
        if vacancy.id == current_vacancy.id:
            continue
        vacancy_words = set(re.findall(r'\w+', vacancy.name.lower()))
        common = current_words & vacancy_words
        if common:
            similar.append((len(common), vacancy))

    similar.sort(reverse=True, key=lambda x: x[0])  # сортировка по совпадениям
    return [v for _, v in similar[:top_n]]
