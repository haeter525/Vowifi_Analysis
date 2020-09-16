# %%
# 讀取切分好的 Csv 檔案
import pandas as pd
import os

sourcePath = '../Dataset/'

dataset = pd.DataFrame()
for root, dirs, files in os.walk(sourcePath):
    print("目錄:", root)
    for f in files:
        if f.split('.')[-1] != 'csv' : continue
        print("檔案:", f)
        source = os.path.join(root, f)
        part = pd.read_csv(source)

        dataset = pd.concat([dataset, part], ignore_index=True)

columnToDrop = [ col for col in dataset.columns if col not in ['Direct','Length','Event','preEvent']]
dataset = dataset.drop(columns=columnToDrop)

# dataset = dataset.drop(dataset[(dataset.Length==158)].index).reset_index().drop(columns='index')
print('完成！')
# %%
# 驗證資料
assert( all( dataset['Direct'].str.match(pat = 'Direction\.((UPWARD)|(DOWNWARD))') ), "Direct 欄位有不正確的值" )
assert( all( dataset['Event'].isin(range(0,14)) ), "Event 欄位有不正確的值" )
assert( all( dataset['preEvent'].isin(range(0,14)) ), "preEvent 欄位有不正確的值" )
print('一切OK！')
# %%
# 將字串根據 Direction 轉換成數值
from lib.Direction import Direction
from lib.Event import Event

for index in range(len(dataset['Direct'])) :
    dataset['Direct'][index] = eval(dataset["Direct"][index]).value

print(dataset)

# %%
# 區分訓練用資料以及測試用資料，並建立決策樹
from sklearn import tree
from sklearn.model_selection import train_test_split

import numpy as np

dataset_numpy = dataset.drop(columns='Event').to_numpy().astype(np.float)

# train_x, test_x, train_y, test_y = train_test_split(dataset_numpy, dataset['Event'].to_numpy().astype(np.float), test_size = 0.3)
train_x = dataset.drop(columns='Event').to_numpy()
train_y = dataset['Event'].to_numpy()

trained_clf = tree.DecisionTreeClassifier(max_depth=7)

print("完成！")

# %%
# 執行訓練
trained_clf = trained_clf.fit(train_x, train_y)
print("訓練 1 次")
# %%
# 儲存訓練模型
import time
from joblib import dump, load

currentTime = time.localtime()
current = f'{currentTime.tm_mon:0>2}{currentTime.tm_mday:0>2}{currentTime.tm_hour:0>2}{currentTime.tm_min:0>2}{currentTime.tm_sec:0>2}'
print(f'目前時間:{currentTime.tm_mon:>2}月{currentTime.tm_mday:>2}日{currentTime.tm_hour:>2}點{currentTime.tm_min:>2}分{currentTime.tm_sec:0>2}秒')
modelFile = f'VowifiParser_v{current}.joblib'
print(f'儲存至:{modelFile}')

dump(trained_clf, modelFile)

# %%
# 讀取訓練模型檔案
from joblib import dump, load
modelFile = input('模型檔案位置:')
trained_clf = load(modelFile)
print('完成！')
# %%
# 測試訓練模型
from lib.Event import EVENT_NAMES, Event
from lib.Direction import DIRECTION_NAMES, Direction

length = int(input('封包長度: '))
assert( length > 0 )

preEvent = input('先決事件: ')
assert( preEvent in EVENT_NAMES, '錯誤事件!' )
preEvent = eval('Event.'+preEvent)

direct = input('傳送方向: ')
assert( direct in EVENT_NAMES, '錯誤方向!')
direct = eval('DIRECTION.'+direct)

# assert(length > 158)
input_x = [[direct.value, length, preEvent.value]]
prediction = trained_clf.predict(input_x)

print(f'[{preEvent}]{direct} {length:>4} -> {EVENT_NAMES[int(prediction[0])]}')
# %%
# 可視化決策樹
from lib.Event import EVENT_NAMES, Event

from IPython.display import Image  
from sklearn import tree
import pydotplus 

dot_data = tree.export_graphviz(trained_clf, out_file=None,
feature_names=['方向', '長度', '先決'],
class_names=EVENT_NAMES,
filled=True, rounded=True,  
special_characters=True)

graph = pydotplus.graph_from_dot_data(dot_data)  
graph.write_png('決策樹.png')
Image(graph.create_png()) 
# %%
# 讀取訓練資料

import os
import pandas as pd

from lib.Direction import Direction

testSource = "../Dataset/預備資料_Wifi_110to240_VOICE_1636_tidyup.csv"
assert( testSource.split('.')[-1]=='csv', "測試資料只接受 CSV 檔案" )

print(f'測試資料: {testSource}')

testset = pd.read_csv(testSource)

columnToDrop = [ col for col in testset.columns if col not in ['Direct','Length','Event','preEvent']]
testset = testset.drop(columns=columnToDrop)
for index in range(len(testset['Direct'])) :
    testset['Direct'][index] = eval(testset["Direct"][index]).value

# testset = testset.drop(testset[testset.Length == 158].index).reset_index().drop(columns='index')

test_x = testset.drop(columns='Event').to_numpy()
test_y = testset['Event'].to_numpy()

print("完成！")

# %%
# 使用測試資料檢測訓練成果
test_y_predicted = trained_clf.predict(test_x)

print(test_y_predicted)
print(test_y)

trained_clf.score(test_x, test_y)

# %%
