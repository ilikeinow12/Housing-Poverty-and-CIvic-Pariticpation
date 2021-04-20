#!/usr/bin/env python
# coding: utf-8

# # Abstract 
# 
# ### Intro
# - 본 분석은 본인의 서울대 사회학과 석사학위 논문에 사용한 자료를 재구성한 것임. 
# - 본 분석에서 이용된 데이터는 <서울시 복지실태조사(2018), 서울연구원>임.본래 논문에서는 2015년도 데이터를 사용했지만 2018년 데이터가 업로드되어 2018년 데이터로 재구성함. 
# - 본래 논문의 목적은 여러 요인들을 통제한 후 주거빈곤과 지역사회참여율 간의 선형관계를 확인하는 것이나, 본 분석에서는 지역사회참여율과 다른 요인들 간의 상관관계를 살펴보는 것으로 한정함. 
# 
# ### 문제 제기  
# - 주거 문제를 한국에서는 개개인의 불평등 관점에서만 논하는 한계가 존재. 
# - 주거안정성과 개인의 사회참여, 정치참여 대한 한국적 맥락에서의 연구 부족.  
# - 특히 서울에 1인가구가 급증하는 상황에서 이 1인가구들의 주거안정성의 파생 결과에 대한 논의 부족.
# 
# ### 가설 설정
# - 주거빈곤이 높을수록 지역사회에 대한 서울시민의 참여도나 참여의향이 떨어질 것이다. 
# 
# 
# ### 분석과정
# 1) Data importing : 서울연구원, 서울시복지싵태조사  
# 2) Data Preprocessing : 분석에 필요한 컬럼들 생성  
# 3) Data Description(Visualization) : 분석 대상인 설문 응답자들의 features를 시각화하여 응답자들의 특성 파악  
# 4) Data Analysis : features간 상관관계 여부 확인, 회귀 분석 진행  
# 5) Conclusion : 분석 결과 정리
# 
# ### 분석 결론 
# - 본 논문은 서울시를 대상으로 주거 빈곤, 주거 요인이 넓게는 지역 사회 통합을, 좁게는 시민들의 지역 사회 참여에 어떤 관계가 있는지 알아보고자 하였다.  
# - 서울시 복지 실태 조사를 통해 주거 요인 - 주거 점유 형태, 거주 건물 유형, 주거 빈곤 지수(슈바베 지수)-와 가구 특성(1인가구, 다인가구, 그외)을 다른 인구, 사회경제적 요인과 회귀 분석한 결과, 주거 요인과 가구 특성은 통계적으로 유의한 영향을 미치는 것으로 나타났다.  
# 구체적으로 다인가구는 1인가구에 비해 지역 사회에 참여 했을 확률이 높았고, 전월세는 자가에 비해 지역 사회에 참여 했을 확률이 낮았다. 한편 기타 유형은 자가에 비해 오히려 확률이 높았다. 다가구/다주택/오피스텔에 사는 사람들은 아파트에 사는 사람들에 비해 지역 사회에 참여 했을 확률이 낮았다.  
#   
# - 이는 곧 주거 문제를 단순히 개개인의 불평등 문제가 아니라 사회 통합의 문제에서도 바라보아야 한다는 점을 시사한다. 지금까지 주거 정책은 1가구 1주택 등의 슬로건과 함께 주거 문제를 재산권의 문제로만 인식하는 한계를 보여주고 있는데, 그 외에도 이웃간의 연대나 공동체 관점도 추가하여 재편해야 함을 논문을 통해 주장하는 바이다. 
# 
# --------------------------------------------------------------------------------------------------------

# ## 1. Data Importing 
# 
# #### 서울시 복지실태조사(2018)
# - 각 칼럼은 설문지의 문제 번호로 명시되어 있음. 각 컬럼의 내용은 서울복지실태조사 서베이 코드북을 통해 확인할 수 있음 
# - 분석에 필요한 컬럼은 각 코드마다 주석처리로 달아놓았음 

# In[2]:


import pandas as pd
import numpy as np

df = pd.read_excel('sisurvey_2018-ER-10_RAWDATA_excel_서울복지실태조사.xlsx')
df = df.set_index('ID')

#xlsx -> csv -> db에 넣는 작업 
#엑셀파일이 행이 많고 null값이 모두 text 타입이라 바로 db에 넣을수가 없음 
#따라서 null값을 숫자998로 채워 int타입으로 바꿔 전체 용량을 줄여주는 작업 수행
#만들어진 csv파일은 db에 업로드함 
df.fillna(998).to_csv('./test.csv')

import pymysql
from table_info import *
 
conn=pymysql.Connect(
    host=host,
    port=port,
    user=user,
    password=password,
    db=db
    )

cursor=conn.cursor()

df=pd.read_sql('select * from raw', conn)
df=df.set_index('ID')
df.replace(998,'NaN', inplace=True)


# ## 2. Data Preprocessing 
# - 본 분석의 목적은 주거 빈곤과 다른 요인들과 지역사회참여율의 상관관계를 살펴보는 것임.
# - 따라서 목적에 맞게 새로운 칼럼들을 추가하여 새로운 데이터셋 생성. 
# - 본 분석에서 필요한 칼럼들(features)은 다음과 같음 : 
# > 설문 응답자의 인구학적 특성 : 성별, 연령, 가구유형  
# 설문 응답자의 사회경제적 특성  : 교육수준, 월평균소득  
# 설문 응답자의 주거 환경 및 주거 빈곤율  : 주거점유형태, 거주건물의 유형, 주거빈곤(슈바베 지수)  
# 설문 응답자의 지역사회참여 : 지역사회 참여경험, 지역사회 참여의향

# ### [1] 설문응답자의 인구학적 특성 : 성별, 연령, 가구유형 

# In[3]:


### 설문응답자의 인구학적 특성: 성별 
# A0111 : 설문 응답 가구원의 번호 (1=가구주, 2=배우자, 3=가구주의 자녀, 4=가구주의 자녀의 배우자, 5=가구주의 부모
# A013~A01304 : 설문 응답 가구원의 성별(1=남자, 2=여자)
# 설문에 응답한 가구원들의 성별을 'gender' 컬럼으로 생성

def gen(df):
    if df['A0111']==1 : return df['A013']
    elif df['A0111']==2 : return df['A01301']
    elif df['A0111']==3 : return df['A01302']
    elif df['A0111']==4 : return df['A01303']
    else : return df['A01304']

df['gender']=df.apply(gen, axis=1)



### 설문응답자의 인구학적 특성: 연령  
# A0111 : 설문 응답 가구원의 번호 (1=가구주, 2=배우자, 3=가구주의 자녀, 4=가구주의 자녀의 배우자, 5=가구주의 부모
# A0141~A014104 : 설문 응답 가구원의 연령
# 설문에 응답한 가구원들의 연령을(2018기준) 'age'컬럼으로 생성 

def age(df):
    if df['A0111']==1 : return 2018-df['A0141']+1
    elif df['A0111']==2 : return 2018-df['A014101']+1
    elif df['A0111']==3 : return 2018-df['A014102']+1
    elif df['A0111']==4 : return 2018-df['A014103']+1
    else : return 2018-df['A014104']+1

df['age']=df.apply(age, axis=1)

### 설문응답자의 인구학적 특성: 가구유형 
# A0110 : 설문 응답자의 가구형태 (1=1인가구, 2=모자가구, 3=부자가구, 4=소년소녀가장 가구, 5=조손가구, 6=기타)
# 설문에 응답한 가구원의 가구유형을 1인가구(1), 다인가구(2), 그외(3)으로 분류하여 'hh_type'컬럼으로 생성 

def householdtype(df):
    if df['A0110']==1 : return 1 
    elif df['A0110']==6 : return 2
    else : return 3 

df['hh_type']=df.apply(householdtype, axis=1)


# ### [2] 설문 응답자의 사회경제적 특성 : 교육수준, 월평균소득

# In[4]:


### 설문응답자의 사회경제적 특성: 교육수준 
# A0111 : 설문 응답 가구원의 번호 (1=가구주, 2=배우자, 3=가구주의 자녀, 4=가구주의 자녀의 배우자, 5=가구주의 부모
# A016~A01603 : 설문 응답 가구원의 최종 학교 (1=미취학, 2=무학, 3=초등학교, 4=중학교, 5=고등학교, 6=대학(4년제미만), 7=대학(4년제이상), 8=대학원(석사), 9=대학원(박사))
# 설문에 응답한 가구원의 교육수준을 'edu'컬럼으로 생성 

def edu(df):
    if df['A0111']==1 : return df['A016']
    elif df['A0111']==2 : return df['A01601']
    elif df['A0111']==3 : return df['A01602']
    elif df['A0111']==4 : return df['A01603']
    else : return df['A01604']

df['edu']=df.apply(edu, axis=1)


### 설문응답자의 사회경제적 특성 : 월평균소득(지난해-2017년-기준) 
# B09 : 가구 총소득_근로소득(만원) 
# B0901 : 가구 총소득_사업소득(만원)
# B0902 : 가구 총소득_재산소득(만원)
# B0903 : 가구 총소득_공적이전소득(만원)
# B0904 : 가구 총소득_사적이전소득/기타소득(만원) 
# 설문에 응답한 가구원의 총 가구연소득을 /12 하여 월소득을 의미하는 'income'컬럼 생성 

df['income']=df.loc[:, 'B09':'B0904'].sum(axis=1) #연소득 
df['income']=df['income']/12   #월평균소득
df['income']=df['income'].round() #반올림 


# ### [3] 설문 응답자의 주거환경 및 주거빈곤 : 주거점유형태, 거주건물유형, 슈바베지수
# <b> 슈바베 지수 Schuwabe's index의 정의</b>
# > - 슈바베 지수(%):월 주거비 지출 / 월 가계 지출 *100  
# > - 가계지출 : 주거비, 생활비, 세금,의료비  
# > - 주거비 : 월세 또는 전세가, 수도세, 전기세 등 관리비, 부채에 대한 한 달 이자   
# >주1) 보증금은 주거비에 포함하지 않음. 이는 보증금을 포함할 경우 보증금 없는 월세 거주자가 보증금이 있는 월세 거주자보다 주거비 부담이 덜 느껴지는 것으로 나타날 소지가 있기 때문. 따라서 본 분석에서 주거비는 보증금을 제외한 월세와 관리비, 부채 한 달 이자를 포함함.  
# >주2) 부채에 대한 한 달 이자는 가구의 총 부채에서 주거비가 1순위 ,2순위인 가구에 한정해 적용 

# In[5]:


### 설문응답자의 주거 점유형태 
# A041 : 거주하고 있는 주택 점유 형태 (1=자가, 2=전세, 3=보증금 있는 월세, 4=보증금 없는 월세, 5=무상, 6=기타)
# 설문에 응답한 가구원 가구의 주택 점유형태를 자가(1), 전세(2), 월세(3), 그외(4)로 분류하여 'occupation'컬럼 생성 

def occupation(df):
    if df['A041']==1 : return 1 
    elif df['A041']==2 : return 2
    elif df['A041']==3 or df['A041']==4 : return 3 
    else : return 4 

df['occupation']=df.apply(occupation, axis=1)



### 설문응답자의 거주건물 유형 
# A03 : 거주하고 있는 주택의 유형 
#(1=일반단독주택, 2=다가구용 단독주택, 3=다세대용 단독주택, 4=연립주택, 
# 5=아파트, 6=오피스텔(원룸제외), 7=원룸, 8=주택이 아닌 건물(쪽방, 고시원, 상가, 여관, 공장 등),
# 9=주택이 아닌 임시구조물(비닐하우스, 움막, 판잣집, 컨테이너 등), 10=기타)

# 설문에 응답한 가구원 가구의 거주건물 유형을 아파트(1), 다가구/다세대/연립주택/오피스텔(2), 단독주택(3), 원룸(4), 그외(5)로 분류하여 
# 'building_type'컬럼 생성 

def buildingtype(df):
    if df['A03']==5 : return 1
    elif df['A03']>=2 and df['A03']<=4 : return 2 
    elif df['A03']==6 : return 2
    elif df['A03']==1 : return 3 
    elif df['A03']==7 : return 4 
    else : return 5
    
df['building_type']=df.apply(buildingtype, axis=1)




###주거빈곤 
##[1] 월 주거비지출 : 부채에 대한 월이자, 관리비(난방비 등), 월세 

#1) 부채에 대한 월이자
# B141 : 보유하고 있는 부채 용도(1순위) : 1= 주택구입비용(거주용), 2=주택 전월세 보증금  
# B14101 : 보유하고 있는 부채 용도(2순위) : 1= 주택구입비용(거주용), 2=주택 전월세 보증금 
# B143 = 부채로 인한 매달 지출 이자(만원) 

# 설문에 응답한 가구원 가구의 부채 원인이 주택구입비용, 전월세보증금비용인 경우에 한하여 매달 지출 이자를 'interest'컬럼으로 생성 

def interest(df):
    if df['B141']==1 or df['B141']==2 : return df['B143']
    if df['B14101']==1 or df['B14101']==2 : return df['B143']
    else : return 0 

df['interest']=df.apply(interest, axis=1)



#2) 월세 
# A0424 : 보증금 없는 월세 거주자 _ 매달 월세(만원) 
# A04232 : 보긍금 있는 월세거주자 _ 매달 월세(만원) 

# 설문에 응답한 가구원 가구의 월세를 'mon_pay' 컬럼으로 생성 

df['A04232'].fillna(0, inplace=True) #Nan -> 0 
df['A0424'].fillna(0, inplace=True)
df['mon_pay']=df['A04232'] + df['A0424']


#3) 난방비 
# A08 : 난방비 지출 금액(만원) 
#난방비가 999인 이상값이 존재하는데, 이는 같은 소득수준에 속하는 가구들의 평균난방비로 대체. 

a=df[df['A08']==999]
a[['A08', 'income']]

in_2300=df[(df['income']>=200) & (df['income']<300)]
in_2300['A08'].mean()

in_3400=df[(df['income']>=300) & (df['income']<400)]
in_3400['A08'].mean()

in_5600=df[(df['income']>=500) & (df['income']<600)]
in_5600['A08'].mean()

df.loc[38:40, 'A08']=15
df.loc[158, 'A08']=16
df.loc[1674, 'A08']=19



# 4) 총 월주거비 지출 = 1)부채에 대한 월이자 +2)월세 +3)난방비  
def h_expense(df):
    if df['occupation']==1 : return df['A08']+df['interest']
    elif df['occupation']==2 : return df['A08']+df['interest']
    elif df['occupation']==3 : return df['mon_pay']+df['A08']+df['interest']
    else : return df['A08']+df['interest']
    
df['h_expense']=df.apply(h_expense, axis=1)


## [2] 월 가계지출비 
# 1) 생활비
# B02 : 가구 한 달 평균 생활비 지출액(만원)
# 이상치(999999) -> 비슷한 소득수준 가구의 월평균 가계지출비로 대체 

b=df[df['B02']==999999]
b['income']

temp=in_2300.drop(38, axis=0)
temp.B02.mean()

df.loc[38, 'B02']=167


# 2) 세금  
# B04 : 2017년 지출 세금 (만원)
# 이상치(999999) -> 비슷한 소득수준 가구의 월평균 세금으로 대체

c=df[df['B04']==999999]
c[['income', 'B04']]

in_0100=df[(df['income']<400)]
temp=in_0100[in_0100.B04!=999999]
temp.B04.mean()

in_1200=df[(df.income>=100)&(df.income<200)]
temp=in_1200[in_1200.B04!=999999]
temp.B04.mean()

in_4500=df[(df.income>=400)&(df.income<500)]
temp=in_4500[in_4500.B04!=999999]
temp.B04.mean()

df.loc[[1111,1805,1806,1809,1812,1813,2326], 'B04']=137
df.loc[2334, 'B04']=81
df.loc[1668, 'B04']=243


# 3) 사회보장제도비 
# B05 : 2017년 사회보장제도 납부 금액(만원) 
#이상치(999999) -> 비슷한 소득수준 가구들의 평균사회보장제도비 

d=df[df.B05==999999]
d[['B05', 'income']]

temp=in_0100[in_0100.B05!=999999]
temp.B05.mean()

temp=in_1200[in_1200.B05!=999999]
temp.B05.mean()

temp=in_4500[in_4500.B05!=999999]
temp.B05.mean()

df.loc[[1111,1805, 1806, 1809, 1812, 1813, 2326], 'B05']=155
df.loc[2334, 'B05']=77
df.loc[1668, 'B05']=279


#4) 월가계지출비 = 1)생활비 +2)세금 +3)사회보장제도비 
df['mon_living_pay']=df['B02']+(df['B04']+df['B05'])/12
df['mon_living_pay']=df['mon_living_pay']



# 주거빈곤율 = 슈바베 지수 
# = 월 주거비 지출 / 월 가계 지출 *100  
df['Schwabe']=df['h_expense']/df['mon_living_pay']*100
df['Schwabe']=df['Schwabe'].round(2)


# ### [4] 설문 응답자의 지역사회참여
# - 지역사회 참여경험 : 주민모임, 지역봉사활동, 마을공동체사업 (1~4점, 높을수록 자주참여함) 
# - 추후 지역사회 참여의향 : 주민모임, 지역봉사활동, 마을공동체사업 (1~5점, 높을수록 자주참여함) 
# 

# In[6]:


# D121 : 최근 1년 간 참여 경험_반상회, 주민회의, 부녀회, 아파트, 대표자 회의, 통반장 회의
# D12101 : 최근 1년 간 참여 경험_지역 방범활동, 청소년선도, 교통정리와 같은 지역봉사활동
# D12102 : 최근 1년 간 참여 경험_마을주민들이 모여 지역문제를 해결하거나 문화 활동을 하는 마을공동체사업
# 1~4점, 높을수록 자주 참여 

# 위의 컬럼들의 평균점수로 지역사회참여경험을 의미하는 'community_part' 컬럼 생성.
# 연속형 변수, 1~4점, 높을수록 경험이 많음 

df['community_part']=(df['D121']+df['D12101']+df['D12102'])/3


# D122 : 향후 참여 의사_반상회, 주민회의, 부녀회, 아파트, 대표자 회의, 통반장 회의
# D12201 : 향후 참여 의사_지역 방범활동, 청소년선도, 교통정리와 같은 지역봉사활동
# D12202 : 향후 참여 의사_마을주민들이 모여 지역문제를 해결하거나 문화 활동을 하는 마을공동체사업
# 1~5점 : 높을수록 참여 의사 높음 

# 위의 컬럼들의 평균점수로 지역사회 추후 참여의향을 의미하는 'community_part_will' 컬럼 생성.
# 연속형 변수, 1~5점, 높을수록 경험이 많음 

df['community_part_will']=(df['D122']+df['D12201']+df['D12202'])/3



#분석을 위한 최종 데이터셋 
df_final=df.loc[:, 'gender':]
df_final.drop(['interest','mon_pay','h_expense','mon_living_pay'], axis=1, inplace=True)


# ### 최종 테이블 -> db의 test table로 

# In[ ]:


# q = '''
#     create table test (
#     ID int,
#     gender float,
#     age float,
#     hh_type int,
#     edu float,
#     income float,
#     occupation int,
#     building_type int, 
#     Schwabe float,
#     community_part float,
#     community_part_will float,
#     age_category char(20),
#     income_category char(100),
#     Schwabe_category char(100)
# );
# '''
# cursor.execute(q)
# conn.commit()

# # sqlalchemy를 이용해 db table(test)로 df_final 삽입. 
# from sqlalchemy import create_engine
# engine = create_engine('mysql+pymysql://root:j8477122@localhost/ssurvey')
# con = engine.connect()

# df_final.to_sql(name='test', con=con, if_exists='append', index_label='ID')


# ## 3. Data Description
# 
# ### 1) 설문 응답자의 성별 
# - 설문 응답자는 여성이 남성보다 더 많았음 : 여성 약 80%, 남성 약 20%
# - 이는 설문이 이루어지는 낮 시간에 여성이 남성보다 주로 더 집에 머물러 있음을 의미.

# In[64]:


#db의 test 테이블 -> df_final로 불러오기 
df_final = pd.read_sql('select * from test', conn)

from matplotlib import rc 
rc('font', family='AppleGothic')
import matplotlib.pyplot as plt 
import seaborn as sns 

fig, ax= plt.subplots(1,1,figsize=(5,5))
sns.countplot(data=df_final, x='gender', palette=["#538790", "#e59998"], ax=ax)
ax.set_title('응답자의 성별분포', fontweight='bold')
ax.set_xticklabels(['남성','여성'])
plt.show()


# ### 2) 설문 응답자의 연령층 
# - 설문 응답자의 연령층은 주로 3~60대를 형성. 
# - 위의 성별 분포와 함께 보았을 때 이는 남성에 비해 상대적으로 여성의 경제활동참여가 낮다는 사실을 반영하는 것이기도 함.

# In[67]:


fig = plt.figure(figsize=(12,10))
ax1=fig.add_subplot(2,1,1)
ax2=fig.add_subplot(2,1,2)

sns.distplot(df_final.age, kde=False, ax=ax1)
ax1.set_title('응답자의 연령분포')

bins=[0,20,31,41,51,61,71,81,100]  
df_final['age_category']=pd.cut(df_final['age'], bins, labels=['10s','20s', '30s', '40s','50s','60s','70s', '80s+'])
sns.countplot(data=df_final, x='age_category', ax=ax2, palette=["#538790", "#e59998"], hue='gender')
ax2.set_title('응답자의 성별 연령분포')

plt.show()


# ### 3) 설문 응답자의 교육수준
# - 고졸 > 대학(4년제이상) > 대학(4년제미만) > 중졸 > 초졸 > 대학원(석사) > 무학 순임. 
# - 응답자의 대다수가 베이비부머 세대 > 30대인 것과 일치하는 분포임. (베비이부머 세대는 대체로 고졸이 많으며 80년대에 태어난 지금의 30대는 한국 사회에서 가장 높은 교육수준을 보여주고 있음) 

# In[70]:


fig, ax= plt.subplots(1,1,figsize=(12,5))
sns.countplot(data=df_final, x='edu',  ax=ax)
ax.set_title('응답자의 교육수준')
ax.set_xticklabels(['무학','초졸','중졸', '고졸', '대학(4년제미만)','대학(4년제이상)','대학원(석사)', '대학원(박사)'])
plt.show()


# ### 4) 설문 응답자의 2017년 가구 평균 월소득(만원) 분포
# - 이상치를 제외한 나머지 대체로 200만원 이상~600만원 미만에 분포.
# - 연령층에 따른 소득분포를 보면 일반적인 생애주기에 따른 소득 분포와 일치함. 한편 6-70대 응답자가 속한 가구는 200만원 미만에 다수 분포하고 있음. 이는 익히 알려진 한국의 노인 빈곤을 반영하고 있음
# - 가구유형별 소득분포를 보면 다인가구는 골고루 분포하고 있고 안정적인 소득을 가지고 있는 것으로 판단되는 반면, 1인가구는 100만원-300만원 미만에 주로 분포하고 있음. 연령별 분포에서 200만원-300만원 미만에 20대~30대 층이 많이 분포하고 있는 것으로 보아 100만원-300만원 미만에 속한 1인가구는 주로 청년층임을 추측할 수 있음. 또한 200만원 미만 소득구간에 속하는 1인가구도 연령별 소득분포로 봤을 때 노인 1인가구임을 추측할 수 있음. 
# - 이러한 분포는 많은 1인가구들이 주로 낮은 소득으로 생활하고 있음을 시사.

# In[73]:


fig = plt.figure(figsize=(15,10))
ax1=fig.add_subplot(2,1,1)
ax2=fig.add_subplot(2,1,2)

bins=[0,100,200, 300, 400, 500, 600, 1000]
df_final['income_category']=pd.cut(df_final['income'], bins)
sns.countplot(data=df_final, x='income_category', ax=ax1, hue='age_category')
ax1.set_title('응답자의 월평균 소득분포(지난해기준, 연령별)')
ax1.set_xticklabels(['100만원미만','100~200만원미만', '200~300만원미만', '300~400만원미만', 
                     '400~500만원미만', '500~600만원미만', '600만원이상'])

sns.countplot(data=df_final, x='income_category', palette =['#E59998', '#FAD8AA', '#538790'], ax=ax2, hue='hh_type')
ax2.set_title('응답자의 월평균 소득분포(지난해기준, 가구유형별)')
ax2.set_xticklabels(['100만원미만','100~200만원미만', '200~300만원미만', '300~400만원미만', 
                     '400~500만원미만', '500~600만원미만', '600만원이상'])
plt.legend(labels=['1인가구', '다인가구', '그외'])
plt.show()


# ### 5) 설문응답자의 주거점유형태 
# 
# - 자가 > 전세 > 월세 > 기타 순 
# - 1인 가구의 경우 전월세가 자가보다 많으며, 다인가구는 자가가 가장 많음. 

# In[74]:


fig, ax= plt.subplots(1,1,figsize=(7,5))
sns.countplot(data=df_final, x='occupation', palette =['#E59998', '#FAD8AA', '#538790'], ax=ax, hue='hh_type')
ax.set_title('가구유형별 주거점유형태')
ax.set_xticklabels(['자가', '전세', '월세', '기타'])
plt.legend(labels=['1인가구', '다인가구', '그외'])
plt.show()


# ### 5) 설문응답자의 거주건물유형
# - 다세대/다가구/연립주택/오피스텔 > 아파트 > 단독주택 > 원룸 > 기타 순
# - 점유유형별로 보면, 자가의 경우 아파트가 가장 많았고 전월세는 다가구/다세대/연립주택/오피스텔이 가장 많았음. 
# - 한국 도시의 일반적인 가구 모습을 잘 반영하고 있음. 
# - 연령, 가구유형, 주거점유형태와 함께 종합해봤을 때 청년층, 노인층 1인가구가 전월세의 형태로 다세대/다가구/연립주택/오피스텔에 많이 거주하는 것으로 보임. 
# - 청년 및 노인 1인가구의 소득수준이 높지 않다는 사실을 고려해보면 이들의 주거안정성이 낮다고 결론지을 수 있음.

# In[75]:


fig, ax1= plt.subplots(figsize=(12,5))
sns.countplot(data=df_final, x='building_type',palette =['#E59998', '#FAD8AA', '#538790'], ax=ax1, hue='hh_type')
ax1.set_title('설문응답자의 거주건물유형(가구유형별)')
ax1.set_xticklabels(['아파트', '다세대/다가구/연립주택/오피스텔', '단독주택', '원룸', '기타'])
plt.legend(labels=['1인가구', '다인가구', '그외'])
plt.show()


# In[76]:


fig, ax2= plt.subplots(figsize=(12,5))
sns.countplot(data=df_final, x='building_type', palette =['#E59998', '#FAD8AA', '#538790', '#040404'], ax=ax2, hue='occupation')
ax2.set_title('설문응답자의 거주건물유형(점유유형별)')
ax2.set_xticklabels(['아파트', '다세대/다가구/연립주택/오피스텔', '단독주택', '원룸', '기타'])
plt.legend(labels=['자가', '전세', '월세', '기타'])
plt.show()


# ### 6) 설문응답자의 주거빈곤율(슈바베지수)
# - 슈바베지수는 수치에 따라 다음과 같이 구분할 수 있음  
# > 25미만 : 주거빈곤낮음  
# 25~60미만 : 주거빈곤높음  
# 60이상 : 주거빈곤심각 
# 
# - 가구유형별로 주거빈곤을 보면 다인가구는 대체로 주거빈곤이 낮으나 1인가구의 경우 주거빈곤이 낮은 경우와 높은 경우의 차이가 크지 않음. 
# - 이는 앞서 1인가구의 주거안정성이 낮다는 사실과 같은 맥락임. 

# In[78]:


fig, ax=plt.subplots(figsize=(7,5))

bins=[0,25,60,500]
df_final['Schwabe_category']=pd.cut(df_final['Schwabe'], bins, labels=['25미만','25~60미만', '60이상'])
sns.countplot(data=df_final, x='Schwabe_category',palette =['#E59998', '#FAD8AA', '#538790'], ax=ax, hue='hh_type') 
ax.set_title("설문응답자의 주거빈곤율")
plt.legend(['1인가구','다인가구', '기타'])
plt.show()


# ### 7) 설문응답자의 지역사회참여 
# > - 지역사회참여경험(1~4점, 높을수록 참여경험 많음)  
# > - 추후 지역사회참여의향(1~5점, 높을수록 참여의향 높음) 
# 
# - 설문응답자들의 지역사회참여는 대체로 낮음. 
# - 지역사회참여와 참여의향간에는 선형관계가 존재하는 것으로 나타남

# In[15]:


fig=plt.figure(figsize=(15,5))
ax1=fig.add_subplot(1,2,1)
ax2=fig.add_subplot(1,2,2)

sns.distplot(df_final['community_part'], kde=False, ax=ax1)
ax1.set_title("설문응답자의 지역사회참여경험")

sns.distplot(df_final['community_part_will'], kde=False, ax=ax2)
ax2.set_title("설문응답자의 추후 지역사회참여의향")
plt.show()


# In[16]:


sns.regplot(data=df_final, x='community_part', y='community_part_will')
plt.title("지역사회참여경험과 추후참여의향")
plt.show()


# ## 4. Data Analysis
# ### 1) 상관관계 분석   
# 
# - 상관관계 분석을 통해 주요 지표인 지역 사회 참여(community_part), 지역 사회 참여 의향(community_part_will)을 제외하고 다른 변수들 간 다중공선성을 확인해본 결과 변수들간 다중공선성은 약하다고 보임.  
# - 따라서 따로 변수를 제거해 줄 필요 없이 그냥 진행하기로 함

# In[59]:


plt.rcParams['axes.unicode_minus'] = False

corr=df_final.loc[:, 'gender':].corr()

f, ax = plt.subplots(figsize=(10, 10))
mask=np.triu(np.ones_like(corr, dtype=np.bool))
cmap = sns.diverging_palette(220,10, as_cmap=True)

ax = sns.heatmap(corr, cmap=cmap, annot=True, vmax=1, square=True, mask=mask, linewidth=.5)
plt.show()


# ### 2) 회귀 분석   
#   
# 1차 분석 : 주거 요인 + 가구 특성 요인만 넣고 분석  
# 2차 분석 : 주거 요인 + 가구 특성 요인 + 인구 사회경제적 요인 모두 넣고 분석
# 
# **<지역 사회 참여 경험>**  
# - 주거 요인만 포함했을 때  
# > 다인가구는 1인가구에 비해 지역 사회에 참여 했을 확률이 높았다.  
# > 전월세는 자가에 비해 지역 사회에 참여 했을 확률이 낮았다. 한편 기타 유형은 자가에 비해 오히려 확률이 높았다. 
# > 다가구/다주택/오피스텔에 사는 사람들은 아파트에 사는 사람들에 비해 지역 사회에 참여 했을 확률이 낮았다. 
#   
#     
# - 주거 요인 + 인구, 사회경제적 요인까지 포함했을 때  
# > 다인가구는 1인가구에 비해 지역 사회에 참여 했을 확률이 높았다.  
# > 전월세는 자가에 비해 지역 사회에 참여 했을 확률이 낮았다. 한편 기타 유형은 자가에 비해 오히려 확률이 높았다. 
# > 다가구/다주택/오피스텔에 사는 사람들은 아파트에 사는 사람들에 비해 지역 사회에 참여 했을 확률이 낮았다.  
#   
#   
# - 정리하자면  
# > 주거 요인은 전반적으로 지역사회 참여 경험에 유의한 영향을 미치는 것으로 나타났다.  
#   
#     
# **<지역 사회 참여 의향>**  
# - 주거 요인만 포함했을 때  
# > 다인가구는 1인가구에 비해 지역 사회에 참여 했을 확률이 높았다.  
# > 전월세는 자가에 비해 지역 사회에 참여 했을 확률이 낮았다. 한편 기타 유형은 자가에 비해 오히려 확률이 높았다. 
# > 다가구/다주택/오피스텔에 사는 사람들은 아파트에 사는 사람들에 비해 지역 사회에 참여 했을 확률이 낮았다.  
#   
#     
# - 주거 요인 + 인구, 사회경제적 요인까지 포함했을 때  
# > 다인가구는 1인가구에 비해 지역 사회에 참여 했을 확률이 높았다.  
# > 전월세는 자가에 비해 지역 사회에 참여 했을 확률이 낮았다. 한편 기타 유형은 자가에 비해 오히려 확률이 높았다. 
# > 다가구/다주택/오피스텔에 사는 사람들은 아파트에 사는 사람들에 비해 지역 사회에 참여 했을 확률이 낮았다.  
#   
#   
# - 정리하자면  
# > 주거 요인은 전반적으로 지역사회 참여 의향에 유의한 영향을 미치는 것으로 나타났다.  
# 

# In[48]:


from statsmodels.formula.api import ols
# 지역 사회 참여 경험 회귀 분석 
# 가구 특성, 주거 요인만 포함했을 때 
fit = ols('community_part ~ C(hh_type) +C(occupation) +C(building_type) +Schwabe', data=df_final).fit()
fit.summary()


# In[49]:


#가구 특성, 주거 요인 +인구 사회경제학적 요인까지 포함 
fit = ols('community_part ~ C(gender) +age +C(hh_type) +C(edu) +income +C(occupation) +C(building_type) +Schwabe', data=df_final).fit()
fit.summary()


# In[60]:


#지역 사회 참여 의향 회귀 분석 
#가구 특성, 주거 요인만 포함 
fit = ols('community_part_will ~ C(hh_type) +C(occupation) +C(building_type) +Schwabe', data=df_final).fit()
fit.summary()


# In[61]:


#가구 특성, 주거 요인 +인구 사회경제학적 요인까지 포함 
fit = ols('community_part ~ C(gender) +age +C(hh_type) +C(edu) +income +C(occupation) +C(building_type) +Schwabe', data=df_final).fit()
fit.summary()


# ## 5. Conclusion 
# - 본 논문은 서울시를 대상으로 주거 빈곤, 주거 요인이 넓게는 지역 사회 통합을, 좁게는 시민들의 지역 사회 참여에 어떤 관계가 있는지 알아보고자 하였다.  
# - 서울시 복지 실태 조사를 통해 주거 요인 - 주거 점유 형태, 거주 건물 유형, 주거 빈곤 지수(슈바베 지수)-와 가구 특성(1인가구, 다인가구, 그외)을 다른 인구, 사회경제적 요인과 회귀 분석한 결과, 주거 요인과 가구 특성은 통계적으로 유의한 영향을 미치는 것으로 나타났다.  
# 구체적으로 다인가구는 1인가구에 비해 지역 사회에 참여 했을 확률이 높았고, 전월세는 자가에 비해 지역 사회에 참여 했을 확률이 낮았다. 한편 기타 유형은 자가에 비해 오히려 확률이 높았다. 다가구/다주택/오피스텔에 사는 사람들은 아파트에 사는 사람들에 비해 지역 사회에 참여 했을 확률이 낮았다.  
#   
# - 이는 곧 주거 문제를 단순히 개개인의 불평등 문제가 아니라 사회 통합의 문제에서도 바라보아야 한다는 점을 시사한다. 지금까지 주거 정책은 1가구 1주택 등의 슬로건과 함께 주거 문제를 재산권의 문제로만 인식하는 한계를 보여주고 있는데, 그 외에도 이웃간의 연대나 공동체 관점도 추가하여 재편해야 함을 논문을 통해 주장하는 바이다. 

# In[ ]:


conn.close()
con.close()


# In[ ]:




