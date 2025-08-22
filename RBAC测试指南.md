# RBAC功能测试指南

## 概述
本文档详细说明了如何测试项目中的"基于角色的访问控制"(RBAC)功能，特别是仓库操作员(Operator)角色的权限控制。

## 已完善的RBAC配置

### 1. 角色权限配置
项目现在支持以下角色：

**医疗数据库角色：**
- `doctor` - 医生（可访问：doctors, patients, medical_records）
- `patient` - 病人（只能访问：doctors）
- `admin` - 管理员（可访问所有表）

**仓储数据库角色：**
- `Manager` - 仓库经理（可访问：warehouse_staff, products, inventory, shipments, locations）
- `Operator` - 仓库操作员（可访问：products, inventory, shipments, locations，但不能查看price和cost列）

**通用角色：**
- `test_user` - 测试用户（有限权限，用于功能测试）

### 2. 用户ID映射
- `D101`, `D102`, `D103`, `D104` → `doctor` 角色
- `S1001` → `Manager` 角色  
- `S1002` → `Operator` 角色
- `test_user` → `test_user` 角色

## 测试方法

### 方法1：使用前端界面测试
1. 启动应用：`python -m app.main`
2. 打开浏览器访问：`http://localhost:8000/static/index.html`
3. 在左侧控制面板选择不同角色进行测试

### 方法2：使用测试脚本
运行提供的测试脚本：
```bash
python test_rbac.py
```

### 方法3：使用API直接测试
使用curl或Postman等工具直接调用API接口。

## 测试用例

### 仓库操作员权限测试

#### 测试1：查询库存信息（应该成功）
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "S1002",
    "role": "Operator",
    "question": "查询所有商品的库存数量",
    "model_type": "auto"
  }'
```
**预期结果：** 权限检查通过，返回库存数据

#### 测试2：查询商品价格（应该失败）
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "S1002",
    "role": "Operator", 
    "question": "查询所有商品的价格信息",
    "model_type": "auto"
  }'
```
**预期结果：** 权限检查失败，提示"试图访问受限列：['price', 'cost']"

#### 测试3：查询商品成本（应该失败）
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "S1002",
    "role": "Operator",
    "question": "查询所有商品的成本信息", 
    "model_type": "auto"
  }'
```
**预期结果：** 权限检查失败，提示"试图访问受限列：['price', 'cost']"

### 仓库经理权限测试

#### 测试4：查询商品价格（应该成功）
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "S1001",
    "role": "Manager",
    "question": "查询所有商品的价格信息",
    "model_type": "auto"
  }'
```
**预期结果：** 权限检查通过，返回价格数据

### 跨数据库权限测试

#### 测试5：医生查询仓库信息（应该失败）
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "D101",
    "role": "doctor",
    "question": "查询仓库库存信息",
    "model_type": "auto"
  }'
```
**预期结果：** 权限检查失败，提示"无权访问表 'inventory'"

## 权限检查机制

### 1. 表级权限控制
- 每个角色都有`allow_tables`列表，定义可访问的表
- 系统会解析SQL语句，提取FROM和JOIN中的表名
- 检查表名是否在允许列表中

### 2. 列级权限控制  
- 每个角色都有`deny_columns`列表，定义被禁止的列
- 系统会检查SQL语句是否包含被禁止的列名
- 如果包含，则拒绝执行

### 3. 动态权限检查
- 在每次SQL执行前进行权限检查
- 根据当前用户角色和数据库类型动态判断权限
- 提供详细的权限拒绝原因

## 测试验证要点

### 1. 权限正确性
- ✅ 仓库操作员能查询库存信息
- ✅ 仓库操作员不能查询价格和成本
- ✅ 仓库经理能查询所有信息
- ✅ 医生不能查询仓库信息

### 2. 错误处理
- ✅ 权限不足时返回明确的错误信息
- ✅ 包含被拒绝列时给出具体提示
- ✅ 跨数据库访问时正确拒绝

### 3. 用户体验
- ✅ 权限检查失败时给出友好提示
- ✅ 错误信息包含具体的权限说明
- ✅ 支持角色自动识别

## 故障排除

### 常见问题

1. **权限检查总是通过**
   - 检查RBAC配置是否正确加载
   - 确认用户角色是否正确识别

2. **权限检查总是失败**
   - 检查数据库连接状态
   - 确认角色权限配置是否正确

3. **列级权限不生效**
   - 检查SQL解析逻辑
   - 确认deny_columns配置

### 调试方法

1. 查看应用日志，确认权限检查过程
2. 使用测试脚本验证各个角色权限
3. 检查前端角色选择是否正确传递

## 总结

通过以上测试，你可以全面验证RBAC功能的完整性。仓库操作员角色现在应该能够：

- ✅ 正常查询库存和商品基本信息
- ❌ 被拒绝查询价格和成本等敏感信息
- ✅ 在权限范围内正常操作
- ❌ 无法越权访问其他数据库的表

如果所有测试用例都通过，说明RBAC功能已经完善并正常工作。
