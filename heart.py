import streamlit as st
import pickle
import base64

st.set_page_config(
    page_title="Saúde do Coração",
    page_icon="❤️"
)

@st.cache_data()
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("pdipaper5.png")
img2 = get_img_as_base64("pdiside.png")

page_bg_img = f"""
<style>
header, footer {{
    visibility: hidden !important;
}}

#MainMenu {{
    visibility: visible !important;
    color: #F44D00;
}}

[data-testid="stAppViewContainer"] > .main {{
    background-image: url("data:fundoesg4k/png;base64,{img}");
    background-size: cover; 
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
[data-testid="stSidebar"] > div:first-child {{
    background-image: url("data:esgfundo1/png;base64,{img2}");
    background-position: center; 
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
    right: 2rem;
}}

.stTextInput>div>div>input[type="text"] {{
    background-color: #C5D6ED; 
    color: #000; 
    border-radius: 7px; 
    border: 2px solid #000010; 
    padding: 5px; 
    width: 500;
}}

@media (max-width: 360px) {{
    [data-testid="stAppViewContainer"] > .main, [data-testid="stSidebar"] > div:first-child {{
        background-size: auto;
    }}
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
st.sidebar.image("Logopdi.png", width=250)

# Welcome text
st.title('Saúde do Coração')
st.write('Aplicativo para verificar a presença de risco de doença cardíaca. Se estiver sentindo '
         'dores no peito ou algo diferente como uma dificuldade em subir escadas ou fazer exercícios, procure um cardiologista!')
st.write('---')
st.write('Insira suas informações de estilo de vida abaixo.')

# Informações do paciente
age = st.number_input('Quantos anos você tem?', 18, 100)
gender_display = st.radio('Qual é o seu gênero?', ['Masculino', 'Feminino'])
height = st.number_input('Qual é a sua altura em cm?', 100, 250)
weight = st.number_input('Quanto você pesa em kg?', 40, 300)
ap_hi = st.number_input('Sua pressão arterial sistólica (PAS)?', 60, 240)
ap_lo = st.number_input('Sua pressão arterial diastólica (PAD)?', 20, 200)
cholesterol = st.selectbox('Seu nível de colesterol?', [1, 2, 3])
gluc = st.selectbox('Seu nível de glicose no sangue?', [1, 2, 3])
smoke = st.checkbox('Você fuma?')
alco = st.checkbox('Você consome álcool?')
active = st.checkbox('Você tem um estilo de vida ativo?')

# Novas perguntas úteis
st.write('---')
st.write('Informações adicionais para uma avaliação mais completa:')
difficulty_stairs = st.checkbox('Você tem dificuldade em subir escadas?')
chest_pain = st.checkbox('Você sente dores no peito ao fazer exercícios?')

# Mapear os valores de gênero para o formato esperado pelo modelo
gender = 'Male' if gender_display == 'Masculino' else 'Female'

# Calculation of additional information
 # BMI
bmi = round(weight / ((height / 100) ** 2), 1)

def categorize_bmi(bmi):
    if bmi < 16:
        return 1
    if 16 <= bmi < 18.5:
        return 2
    if 18.5 <= bmi <= 24.9:
        return 3
    if 25 <= bmi <= 29.9:
        return 4
    if 30 <= bmi <= 34.9:
        return 5
    if 35 <= bmi <= 39.9:
        return 6
    if bmi >= 40:
        return 7

bmi_category = categorize_bmi(bmi)

 # Hypertension
def hypertension(ap_hi, ap_lo):
    if ap_hi < 120 and ap_lo < 80:
        return 1
    if 120 <= ap_hi < 130 and 80 <= ap_lo < 85:
        return 2
    if 130 <= ap_hi < 140 and 85 <= ap_lo < 90:
        return 3
    if 140 <= ap_hi < 160 and 90 <= ap_lo < 100:
        return 4
    if ap_hi >= 160 and ap_lo >= 100:
        return 5
    if ap_hi >= 140 and ap_lo < 90:
        return 6
    return 7

hypertension = hypertension(ap_hi, ap_lo)

# Conversion values to binary
def gender_to_bin(gender):
    if gender == 'Male':
        return 0
    return 1

def bool_to_bin(bool_value):
    if bool_value == False:
        return 0
    return 1

gender = gender_to_bin(gender)
smoke = bool_to_bin(smoke)
alco = bool_to_bin(alco)
active = bool_to_bin(active)

# Model
def load():
    with open ('model.pcl', 'rb') as fid:
        return pickle.load(fid)

features_test = [[age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active, bmi_category, hypertension]]
model = load()
predict = model.predict_proba(features_test)[:, 1][0]

# Ajuste de risco baseado nas perguntas adicionais
risk_adjustment = 0
if difficulty_stairs:
    risk_adjustment += 0.05  # Aumenta o risco em 5% se tiver dificuldade em subir escadas
if chest_pain:
    risk_adjustment += 0.1  # Aumenta o risco em 10% se tiver dores no peito ao fazer exercícios
# Ajuste de risco baseado nas variáveis de estilo de vida
lifestyle_adjustment = 0

# Aumentar o risco para fumantes e consumidores de álcool (valores baseados em estudos)
if smoke:
    lifestyle_adjustment += 0.17  # Aumenta o risco em até 30% para fumantes
if alco:
    lifestyle_adjustment += 0.09  # Aumenta o risco em até 15% para consumo excessivo de álcool

# Reduzir o risco se o paciente for ativo fisicamente
if active:
    lifestyle_adjustment -= 0.15  # Diminui o risco em até 25% para quem faz atividade física regular

# Ajustar o risco previsto
adjusted_predict = min(max(predict + lifestyle_adjustment + risk_adjustment, 0.0), 1.0)  # Garantir que o risco ajustado fique entre 0% e 100%
 # Garantir que o risco ajustado não ultrapasse 100%

# Results
st.write('---')
if st.button('Calcular Probabilidade'):
    st.subheader('***Seus resultados:***')
    if adjusted_predict > 0.5:
        st.error('**Seu risco de doenças cardíacas: {:.2%}**'.format(adjusted_predict))
        st.write('Atenção❗Você está em alto risco de doença cardíaca! 💔')
        # Detalhes sobre hipertensão e outros fatores de risco
        if hypertension == 4:
            st.write('- Você tem hipertensão grau 1. Preste atenção à sua pressão arterial. Consulte um cardiologista!')
        if hypertension == 5:
            st.write('- Você tem hipertensão grau 2. Preste atenção à sua pressão arterial. Consulte um cardiologista!')
        if hypertension == 6:
            st.write('- Você tem hipertensão sistólica isolada. Preste atenção à sua pressão arterial. Consulte um cardiologista!')
        if hypertension == 7:
            st.write('- Você tem uma diferença incomum entre suas leituras de pressão arterial sistólica e diastólica. Isso é um motivo para consultar um cardiologista!')
        if age >= 50:
            st.write('- Você tem mais de 50 anos, o que significa que você está em risco de doença cardíaca devido à idade.')
        if cholesterol == 2:
            st.write('- Seu nível de colesterol é 2. Isso significa que você tem um risco moderado de desenvolver aterosclerose vascular, que afeta a presença de doenças cardíacas. Consulte um terapeuta!')
        if cholesterol == 3:
            st.write('- Seu nível de colesterol é 3. Isso significa que você tem um alto risco de desenvolver aterosclerose vascular, que afeta a presença de doenças cardíacas. Consulte um terapeuta!')
    
    elif 0.3 < adjusted_predict <= 0.5:
        st.warning('**Seu risco de doenças cardíacas é moderado: {:.2%}**'.format(adjusted_predict))
        st.write('Você está em risco moderado de doença cardíaca. 🌡️')
        st.write('Recomendamos melhorar sua dieta, manter uma rotina de exercícios e consultar um cardiologista para uma avaliação mais detalhada.')

    else:
        st.success('**Seu risco de doenças cardíacas: {:.2%}**'.format(adjusted_predict))
        st.write('Ótimo! Parece que você não está em risco de doença cardíaca! 😎')

# Recomendação da OMS
st.write('---')
st.write('### Recomendações da Organização Mundial da Saúde (OMS) para um Coração Saudável:')
st.write('- **Mantenha uma alimentação equilibrada**: Inclua muitas frutas, verduras, legumes, grãos integrais e proteínas magras. Limite o consumo de sal, açúcar e gorduras saturadas.')
st.write('- **Exercite-se regularmente**: A OMS recomenda pelo menos 150 minutos de atividade física moderada ou 75 minutos de atividade física intensa por semana.')
st.write('- **Evite o consumo de tabaco e álcool**: Parar de fumar e moderar o consumo de álcool são passos importantes para a saúde do coração.')
st.write('- **Monitore sua saúde regularmente**: Faça check-ups regulares, monitore sua pressão arterial, colesterol e níveis de glicose.')

# Aqui podemos adicionar algo adicional com base nas novas perguntas
st.write('---')
if difficulty_stairs:
    st.write('⚠️ Sua dificuldade em subir escadas pode ser um sinal de problemas cardíacos. Recomendamos procurar um cardiologista.')
if chest_pain:
    st.write('⚠️ Dores no peito durante exercícios podem ser um sinal de problemas cardíacos. Recomendamos procurar um cardiologista.')
st.write('---')
st.markdown("Desenvolvido por [PedroFS](https://linktr.ee/Pedrofsf)")
