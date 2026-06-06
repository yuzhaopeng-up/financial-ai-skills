# 金融AI的隐私保护：数据不出域的3种方案

> 方法论：金融数据隐私保护 | 联邦学习 | 差分隐私 | 同态加密

## 金融数据的特殊性

银行数据是"敏感中的敏感"：

- **客户信息**：姓名、身份证、手机号
- **交易数据**：金额、时间、对手方
- **资产信息**：存款、理财、贷款
- **行为数据**：交易习惯、偏好、位置

**监管要求**：
- 《个人信息保护法》：数据最小化、目的明确
- 《数据安全法》：分类分级保护
- 央行规定：核心数据不得出境

## 方案一：联邦学习

### 原理

```
传统机器学习:                联邦学习:
┌─────────┐                ┌─────────┐
│ 银行A   │                │ 银行A   │
│ 数据    │ ──→ 中心      │ 数据    │ ──┐
└─────────┘    服务器      └─────────┘   │
                          ┌─────────┐   │
┌─────────┐              │ 银行B   │   │
│ 银行B   │ ──→ 训练     │ 数据    │ ──┤
│ 数据    │              └─────────┘   │ 聚合
└─────────┘              ┌─────────┐   │ 模型
                         │ 银行C   │   │
                         │ 数据    │ ──┘
                         └─────────┘
```

**核心**：数据不动，模型动。各银行本地训练，只上传模型参数。

### 代码示例

```python
# 联邦学习框架 (简化版)
class FederatedLearning:
    def __init__(self, banks: List[Bank]):
        self.banks = banks
        self.global_model = None
    
    def train_round(self):
        """一轮联邦训练"""
        local_models = []
        
        # 各银行本地训练
        for bank in self.banks:
            local_model = bank.local_train(self.global_model)
            local_models.append(local_model)
        
        # 聚合模型 (FedAvg)
        self.global_model = self.aggregate(local_models)
        
        return self.global_model
    
    def aggregate(self, local_models: List[Model]) -> Model:
        """联邦平均"""
        global_weights = {}
        
        for key in local_models[0].weights.keys():
            # 加权平均
            weighted_sum = sum(
                model.weights[key] * model.data_size
                for model in local_models
            )
            total_size = sum(model.data_size for model in local_models)
            global_weights[key] = weighted_sum / total_size
        
        return Model(weights=global_weights)
```

### 适用场景

- 反欺诈模型训练（多家银行联合）
- 信用评分模型优化
- 客户画像共建

## 方案二：差分隐私

### 原理

在数据或模型中添加"噪声"，使得无法反推原始数据。

```
原始数据:                    差分隐私后:
姓名  收入                   姓名  收入
张三  10000        →        张三  10234 (加噪声)
李四  20000                  李四  19876 (加噪声)
王五  15000                  王五  15123 (加噪声)
```

### 代码示例

```python
import numpy as np

class DifferentialPrivacy:
    def __init__(self, epsilon: float = 1.0):
        """
        epsilon: 隐私预算，越小隐私保护越强
        """
        self.epsilon = epsilon
    
    def add_noise(self, data: np.ndarray, sensitivity: float) -> np.ndarray:
        """
        添加拉普拉斯噪声
        
        Args:
            data: 原始数据
            sensitivity: 敏感度（最大变化量）
        """
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale, data.shape)
        return data + noise
    
    def privatize_query(self, query_result: float, 
                        sensitivity: float) -> float:
        """
        对查询结果添加噪声
        """
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return query_result + noise

# 使用示例
dp = DifferentialPrivacy(epsilon=1.0)

# 查询平均收入 (敏感度 = 最大收入 / 人数)
avg_income = 15000
sensitivity = 50000 / 1000  # 假设最大收入5万，1000人

private_avg = dp.privatize_query(avg_income, sensitivity)
print(f"原始结果: {avg_income}")
print(f"隐私结果: {private_avg}")
```

### 适用场景

- 统计数据发布
- 模型训练数据保护
- 查询接口保护

## 方案三：同态加密

### 原理

在加密数据上直接计算，结果解密后与明文计算一致。

```
明文计算:                    密文计算:
2 + 3 = 5                   E(2) + E(3) = E(5)
                            ↓ 解密
                            5
```

### 代码示例

```python
# 使用TenSEAL库 (简化示例)
import tenseal as ts

class HomomorphicEncryption:
    def __init__(self):
        # 创建同态加密上下文
        self.context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
        )
        self.context.global_scale = 2**40
        self.context.generate_galois_keys()
    
    def encrypt(self, data: list) -> ts.CKKSVector:
        """加密数据"""
        return ts.ckks_vector(self.context, data)
    
    def decrypt(self, encrypted: ts.CKKSVector) -> list:
        """解密数据"""
        return encrypted.decrypt()
    
    def compute(self, encrypted_a: ts.CKKSVector, 
                encrypted_b: ts.CKKSVector,
                operation: str = "add") -> ts.CKKSVector:
        """
        密文计算
        
        支持: add, multiply, dot_product
        """
        if operation == "add":
            return encrypted_a + encrypted_b
        elif operation == "multiply":
            return encrypted_a * encrypted_b
        else:
            raise ValueError(f"不支持的操作: {operation}")

# 使用示例
he = HomomorphicEncryption()

# 银行A加密数据
bank_a_data = [10000, 20000, 15000]
encrypted_a = he.encrypt(bank_a_data)

# 银行B加密数据
bank_b_data = [5000, 10000, 8000]
encrypted_b = he.encrypt(bank_b_data)

# 密文计算 (无需解密)
encrypted_sum = he.compute(encrypted_a, encrypted_b, "add")

# 只有授权方才能解密
result = he.decrypt(encrypted_sum)
print(f"加密计算结果: {result}")
```

### 适用场景

- 联合统计计算
- 隐私保护机器学习
- 安全多方计算

## 三种方案对比

| 维度 | 联邦学习 | 差分隐私 | 同态加密 |
|------|----------|----------|----------|
| 数据位置 | 本地 | 本地/中心 | 本地 |
| 计算位置 | 本地+聚合 | 本地 | 密文上 |
| 通信开销 | 中 | 低 | 高 |
| 计算开销 | 低 | 低 | 高 |
| 精度损失 | 无 | 有 | 小 |
| 实现复杂度 | 中 | 低 | 高 |
| 适用场景 | 模型训练 | 统计查询 | 安全计算 |

## 银行实践建议

### 场景选择

```
反欺诈模型训练 → 联邦学习
监管报表统计 → 差分隐私
联合风控计算 → 同态加密
```

### 实施路径

**第一步：评估（1个月）**
- 识别敏感数据场景
- 评估技术可行性
- 制定隐私预算

**第二步：试点（2-3个月）**
- 选择1-2个场景
- 小规模验证
- 效果评估

**第三步：推广（3-6个月）**
- 扩展到更多场景
- 建立治理机制
- 持续优化

## 合规要点

| 法规 | 要求 | 技术对应 |
|------|------|----------|
| 个人信息保护法 | 最小必要原则 | 数据脱敏 |
| 数据安全法 | 分类分级保护 | 访问控制 |
| 央行规定 | 核心数据不出域 | 联邦学习 |
| GDPR | 隐私设计 | 差分隐私 |

---

**#隐私保护 #联邦学习 #差分隐私 #同态加密 #金融合规**
