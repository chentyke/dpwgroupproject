import pandas as pd
import numpy as np
import glob
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

import matplotlib.pyplot as plt

# =========================
# 1. 读取 2015-2022 全部数据
# =========================

files = glob.glob('./players_*.csv')

files = [
    f for f in files
    if os.path.basename(f) in [
        'players_15.csv', 'players_16.csv', 'players_17.csv', 'players_18.csv',
        'players_19.csv', 'players_20.csv', 'players_21.csv', 'players_22.csv'
    ]
]

files.sort()
print("匹配到的文件：", files)

def label_injury_status(traits):
    if pd.isna(traits):
        return -1
    t = str(traits).lower()
    if 'injury prone' in t:
        return 1
    elif 'solid player' in t:
        return 0
    else:
        return -1

dfs = []

for f in files:
    print("正在读取：", f)
    df = pd.read_csv(f, low_memory=False)
    
    year = int(os.path.basename(f).split('_')[1].split('.')[0]) + 2000
    df['season'] = year
    df['injury_status'] = df['player_traits'].apply(label_injury_status)
    
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# 用 sofifa_id 作为球员唯一识别码
player_key = 'sofifa_id'

df_all.sort_values(by=[player_key, 'season'], inplace=True)
df_all.reset_index(drop=True, inplace=True)

print("合并完成：", df_all.shape)
print("injury_status 分布：")
print(df_all['injury_status'].value_counts())

# =========================
# 2. 构造未来标签
# =========================
# 对每个球员，判断当前年份之后是否出现过 injury_status = 1 或 0

def add_future_labels(group):
    group = group.sort_values('season').copy()
    statuses = group['injury_status'].values
    
    future_injury_list = []
    future_solid_list = []
    has_future_record_list = []
    
    for i in range(len(group)):
        future_statuses = statuses[i+1:]
        
        has_future_record = len(future_statuses) > 0
        future_injury = int((future_statuses == 1).any())
        future_solid = int((future_statuses == 0).any())
        
        has_future_record_list.append(has_future_record)
        future_injury_list.append(future_injury)
        future_solid_list.append(future_solid)
    
    group['has_future_record'] = has_future_record_list
    group['future_injury'] = future_injury_list
    group['future_solid'] = future_solid_list
    
    return group

df_all = df_all.groupby(player_key, group_keys=False).apply(add_future_labels)

print("未来标签构造完成。")

# =========================
# 3. 选择特征
# =========================

features = [
    'age', 'height_cm', 'weight_kg',
    'overall', 'potential',
    'pace', 'shooting', 'passing',
    'dribbling', 'defending', 'physic',
    'attacking_crossing',
    'attacking_finishing',
    'attacking_heading_accuracy',
    'attacking_short_passing',
    'attacking_volleys',
    'skill_dribbling',
    'skill_curve',
    'skill_fk_accuracy',
    'skill_long_passing',
    'skill_ball_control',
    'movement_acceleration',
    'movement_sprint_speed',
    'movement_agility',
    'movement_reactions',
    'movement_balance',
    'power_shot_power',
    'power_jumping',
    'power_stamina',
    'power_strength',
    'power_long_shots',
    'mentality_aggression',
    'mentality_interceptions',
    'mentality_positioning',
    'mentality_vision',
    'mentality_penalties',
    'mentality_composure',
    'defending_marking_awareness',
    'defending_standing_tackle',
    'defending_sliding_tackle'
]

# 只保留数据里真实存在的列
features = [c for c in features if c in df_all.columns]
print("最终使用特征数量：", len(features))
print(features)

# =========================
# 4. 只选早期 status = -1 的记录做未来预测模型
# =========================
# 2022 年没有未来年份，所以不能用于验证未来变化
# has_future_record=True 保证这个球员后面还有年份数据

df_unknown_future = df_all[
    (df_all['injury_status'] == -1) &
    (df_all['has_future_record'] == True)
].copy()

print("用于未来转化分析的 -1 样本数量：", df_unknown_future.shape)
print("future_injury 分布：")
print(df_unknown_future['future_injury'].value_counts())
print("future_solid 分布：")
print(df_unknown_future['future_solid'].value_counts())

X_unknown = df_unknown_future[features].apply(pd.to_numeric, errors='coerce')
X_unknown = X_unknown.fillna(X_unknown.mean())

# =========================
# 5. 定义训练函数
# =========================

def train_future_model(X, y, model_name):
    print("\n============================")
    print(f"开始训练：{model_name}")
    print("============================")
    print("目标变量分布：")
    print(y.value_counts())
    
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.3,
        random_state=42,
        stratify=y
    )
    
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced',
        max_depth=8
    )
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    print(f"\n{model_name} 分类报告：")
    print(classification_report(y_test, y_pred))
    
    print(f"{model_name} 混淆矩阵：")
    print(confusion_matrix(y_test, y_pred))
    
    importances = pd.Series(
        model.feature_importances_,
        index=features
    ).sort_values(ascending=False)
    
    print(f"\n{model_name} 影响因素 Top 15：")
    print(importances.head(15))
    
    plt.figure(figsize=(10, 6))
    plt.barh(importances.head(15).index, importances.head(15).values)
    plt.xlabel("Feature Importance")
    plt.ylabel("Features")
    plt.title(f"Top 15 Feature Importance - {model_name}")
    plt.gca().invert_yaxis()
    plt.show()
    
    return model, importances

# =========================
# 6. 训练 Future Injury Model
# =========================

y_future_injury = df_unknown_future['future_injury']

injury_model, injury_importances = train_future_model(
    X_unknown,
    y_future_injury,
    "Future Injury Model"
)

# =========================
# 7. 训练 Future Solid Model
# =========================

y_future_solid = df_unknown_future['future_solid']

solid_model, solid_importances = train_future_model(
    X_unknown,
    y_future_solid,
    "Future Solid Model"
)

# =========================
# 8. 把模型套回所有 -1 样本上，生成预测概率
# =========================

df_unknown_future['future_injury_prob'] = injury_model.predict_proba(X_unknown)[:, 1]
df_unknown_future['future_solid_prob'] = solid_model.predict_proba(X_unknown)[:, 1]

print("\n预测完成。")

# =========================
# 9. 检查：早年 -1 且高 injury 概率，后面是否真的变成 injury
# =========================

injury_threshold = df_unknown_future['future_injury_prob'].quantile(0.90)

high_injury_risk = df_unknown_future[
    df_unknown_future['future_injury_prob'] >= injury_threshold
].copy()

print("\n============================")
print("高 Injury 风险组验证")
print("============================")
print("高风险阈值：", injury_threshold)
print("高风险组样本数：", high_injury_risk.shape[0])
print("高风险组未来真的变成 injury 的比例：")
print(high_injury_risk['future_injury'].mean())

print("全体 -1 样本未来变成 injury 的基础比例：")
print(df_unknown_future['future_injury'].mean())

# =========================
# 10. 检查：早年 -1 且高 solid 概率，后面是否真的变成 solid
# =========================

solid_threshold = df_unknown_future['future_solid_prob'].quantile(0.90)

high_solid_risk = df_unknown_future[
    df_unknown_future['future_solid_prob'] >= solid_threshold
].copy()

print("\n============================")
print("高 Solid 可能组验证")
print("============================")
print("高 Solid 阈值：", solid_threshold)
print("高 Solid 组样本数：", high_solid_risk.shape[0])
print("高 Solid 组未来真的变成 solid 的比例：")
print(high_solid_risk['future_solid'].mean())

print("全体 -1 样本未来变成 solid 的基础比例：")
print(df_unknown_future['future_solid'].mean())

# =========================
# 11. 自动找出 injury 的真实例子
# =========================

injury_examples = high_injury_risk[
    high_injury_risk['future_injury'] == 1
].sort_values(by='future_injury_prob', ascending=False)

print("\n============================")
print("早年 -1，但模型判断高 injury 风险，后面真的变成 injury 的例子")
print("============================")

print(injury_examples[
    [player_key, 'short_name', 'long_name', 'season', 'age',
     'overall', 'physic', 'defending', 'pace',
     'injury_status', 'future_injury_prob', 'future_injury']
].head(20))

# =========================
# 12. 自动找出 solid 的真实例子
# =========================

solid_examples = high_solid_risk[
    high_solid_risk['future_solid'] == 1
].sort_values(by='future_solid_prob', ascending=False)

print("\n============================")
print("早年 -1，但模型判断高 solid 可能，后面真的变成 solid 的例子")
print("============================")

print(solid_examples[
    [player_key, 'short_name', 'long_name', 'season', 'age',
     'overall', 'physic', 'defending', 'pace',
     'injury_status', 'future_solid_prob', 'future_solid']
].head(20))

# =========================
# 13. 查看某个球员完整时间线
# =========================

def show_player_timeline_by_id(pid):
    timeline = df_all[df_all[player_key] == pid].sort_values('season').copy()
    
    # 把预测概率合并回来
    probs = df_unknown_future[
        [player_key, 'season', 'future_injury_prob', 'future_solid_prob']
    ]
    
    timeline = timeline.merge(
        probs,
        on=[player_key, 'season'],
        how='left'
    )
    
    return timeline[
        [player_key, 'short_name', 'long_name', 'season', 'age',
         'overall', 'physic', 'defending', 'pace',
         'injury_status', 'future_injury_prob', 'future_solid_prob']
    ]

# 示例：查看 injury_examples 里第一个球员的完整时间线
if len(injury_examples) > 0:
    example_pid = injury_examples.iloc[0][player_key]
    print("\n第一个 injury 例子的完整时间线：")
    display(show_player_timeline_by_id(example_pid))

# 示例：查看 solid_examples 里第一个球员的完整时间线
if len(solid_examples) > 0:
    example_pid = solid_examples.iloc[0][player_key]
    print("\n第一个 solid 例子的完整时间线：")
    display(show_player_timeline_by_id(example_pid))