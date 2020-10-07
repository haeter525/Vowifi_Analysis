# %%
# imports
import IPython.display
import joblib
import os
import pandas
import pydotplus
import sklearn
import sklearn.tree
import time

from lib.Direction import DIRECTION_NAMES, Direction
from lib.Event import EVENT_NAMES, Event

# %%
# 讀取切分好的 Csv 檔案
sourcePath = 'Dataset/'

dataset = pandas.DataFrame()
for root, dirs, files in os.walk(sourcePath):
    print("目錄:", root)
    for f in files:
        if f.split('.')[-1] != 'csv':
            continue
        print("檔案:", f)
        source = os.path.join(root, f)
        part = pandas.read_csv(source)

        dataset = pandas.concat([dataset, part], ignore_index=True)

columnToDrop = [col for col in dataset.columns if col not in [
    'Direct', 'Length', 'Event', 'preEvent']]
dataset = dataset.drop(columns=columnToDrop)

dataset = dataset.drop(
    dataset[(dataset.Length < 190)].index).reset_index().drop(columns='index')
print('完成！')

# %%
# 驗證資料
assert(all(dataset['Direct'].str.match(
    pat='Direction\.((UPWARD)|(DOWNWARD))')), "Direct 欄位有不正確的值")
assert(all(dataset['Event'].isin(range(0, 14))), "Event 欄位有不正確的值")
assert(all(dataset['preEvent'].isin(range(0, 14))), "preEvent 欄位有不正確的值")
print('一切OK！')

# %%
# 準備資料，將字串根據 Direction 轉換成數值
for index in range(len(dataset['Direct'])):
    dataset['Direct'][index] = eval(dataset["Direct"][index]).value

print(dataset)

train_x = dataset.drop(columns='Event').to_numpy()
train_y = dataset['Event'].to_numpy()

# %%
# 建立決策樹
trained_clf = sklearn.tree.DecisionTreeClassifier(max_depth=7)
print("建立決策樹！")

# %%
# 執行訓練
times = input('次數')
times = 1 if times == "" else int(times)

print(f'訓練{times}次...', end='')
for _ in range(times):
    trained_clf = trained_clf.fit(train_x, train_y)
print('完成')

# %%
# 儲存訓練模型
currentTime = time.localtime()
current = f'{currentTime.tm_mon:0>2}{currentTime.tm_mday:0>2}{currentTime.tm_hour:0>2}{currentTime.tm_min:0>2}{currentTime.tm_sec:0>2}'
print(f'目前時間:{currentTime.tm_mon:>2}月{currentTime.tm_mday:>2}日{currentTime.tm_hour:>2}點{currentTime.tm_min:>2}分{currentTime.tm_sec:0>2}秒')
modelFile = f'Model/VowifiParser_v{current}.joblib'
print(f'儲存至:{modelFile}')

joblib.dump(trained_clf, modelFile)

# %%
# 讀取訓練模型檔案
modelFile = input('模型檔案位置:')
trained_clf = joblib.load(modelFile)
print('完成！')

# %%
# 可視化決策樹
dot_data = sklearn.tree.export_graphviz(trained_clf, out_file=None,
                                        feature_names=['方向', '長度', '先決'],
                                        class_names=EVENT_NAMES,
                                        filled=True, rounded=True,
                                        special_characters=True)

graph = pydotplus.graph_from_dot_data(dot_data)
graph.write_png('決策樹.png')
IPython.display.Image(graph.create_png())
# %%
# 使用訓練資料檢驗
testSource = "Dataset/預備資料_Wifi_110to240_VOICE_1635_tidyup.csv"
assert(testSource.split('.')[-1] == 'csv', "測試資料只接受 CSV 檔案")

print(f'測試資料: {testSource}')

testset = pandas.read_csv(testSource)

columnToDrop = [col for col in testset.columns if col not in [
    'Direct', 'Length', 'Event', 'preEvent']]
testset = testset.drop(columns=columnToDrop)
for index in range(len(testset['Direct'])):
    testset['Direct'][index] = eval(testset["Direct"][index]).value

testset = testset.drop(
    testset[testset.Length < 190].index).reset_index().drop(columns='index')

test_x = testset.drop(columns='Event').to_numpy()
test_y = testset['Event'].to_numpy()

print("完成！")

test_y_predicted = trained_clf.predict(test_x)

print(test_y_predicted)
print(test_y)

trained_clf.score(test_x, test_y)

# %%
# 模型轉換成為 Java code
class_name = 'StateTracer'
method_name = 'nextState'

porter = sklearn_porter.Porter(trained_clf, language='Java')
output = porter.export(class_name, method_name)

f = open(class_name + '.java', 'w')
f.write(output)
f.close()
print('完成！')
# %%
