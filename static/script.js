// 全局变量
let currentDatabase = 'hospital';
let currentUser = 'D101';
let currentModelType = 'auto';  // auto, local, cloud
let currentCloudModel = 'deepseek-r1';

// DOM 元素
const dbSelect = document.getElementById('db-select');
const roleSelect = document.getElementById('role-select');
const questionInput = document.getElementById('question-input');
const sendBtn = document.getElementById('send-btn');
const chatMessages = document.getElementById('chat-messages');
const testConnectionBtn = document.getElementById('test-connection');
const hospitalStatus = document.getElementById('hospital-status');
const warehouseStatus = document.getElementById('warehouse-status');
const loading = document.getElementById('loading');

// 模型选择相关元素
const modelTypeRadios = document.querySelectorAll('input[name="model-type"]');
const cloudModelSelect = document.getElementById('cloud-model-select');
const localModelStatus = document.getElementById('local-model-status');
const cloudModelStatus = document.getElementById('cloud-model-status');
const testModelsBtn = document.getElementById('test-models');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    testDatabaseConnections();
});

// 初始化应用
function initializeApp() {
    // 设置默认值
    dbSelect.value = currentDatabase;
    roleSelect.value = currentUser;
    
    // 更新角色选项
    updateRoleOptions();
    
    // 测试模型状态
    testModels();
}

// 设置事件监听器
function setupEventListeners() {
    // 数据库切换
    dbSelect.addEventListener('change', function() {
        currentDatabase = this.value;
        switchDatabase(currentDatabase);
        updateRoleOptions();
    });

    // 角色切换
    roleSelect.addEventListener('change', function() {
        currentUser = this.value;
    });

    // 模型类型选择
    modelTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            currentModelType = this.value;
            updateModelSelector();
        });
    });

    // 云端模型选择
    if (cloudModelSelect) {
        cloudModelSelect.addEventListener('change', function() {
            currentCloudModel = this.value;
            switchCloudModel(currentCloudModel);
        });
    }

    // 发送消息
    sendBtn.addEventListener('click', sendMessage);
    questionInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 测试连接
    testConnectionBtn.addEventListener('click', testDatabaseConnections);

    // 测试模型
    if (testModelsBtn) {
        testModelsBtn.addEventListener('click', testModels);
    }

    // 快速示例
    document.querySelectorAll('.example-item').forEach(item => {
        item.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            questionInput.value = question;
            questionInput.focus();
        });
    });
}

// 更新角色选项
function updateRoleOptions() {
    const roleSelect = document.getElementById('role-select');
    roleSelect.innerHTML = '';

    if (currentDatabase === 'hospital') {
        const hospitalRoles = [
            { value: 'D101', label: '👨‍⚕️ 医生 (D101)' },
            { value: 'D102', label: '👩‍⚕️ 医生 (D102)' },
            { value: 'D103', label: '👨‍⚕️ 医生 (D103)' },
            { value: 'D104', label: '👩‍⚕️ 医生 (D104)' },
            { value: 'test_user', label: '👤 普通用户' }
        ];
        
        hospitalRoles.forEach(role => {
            const option = document.createElement('option');
            option.value = role.value;
            option.textContent = role.label;
            roleSelect.appendChild(option);
        });
    } else {
        const warehouseRoles = [
            { value: 'S1001', label: '👨‍💼 仓库经理 (S1001)' },
            {value: 'S1002', label: '👷 仓库操作员 (S1002)' },
            { value: 'S1003', label: '👷 仓库操作员 (S1003)' },
            { value: 'S1004', label: '👷 仓库操作员 (S1004)' },
            { value: 'test_user', label: '👤 普通用户' }
        ];
        
        warehouseRoles.forEach(role => {
            const option = document.createElement('option');
            option.value = role.value;
            option.textContent = role.label;
            roleSelect.appendChild(option);
        });
    }

    // 设置默认角色
    roleSelect.value = currentUser;
}

// 更新模型选择器显示
function updateModelSelector() {
    const cloudSelector = document.querySelector('.cloud-model-selector');
    if (currentModelType === 'cloud') {
        cloudSelector.style.display = 'block';
    } else {
        cloudSelector.style.display = 'none';
    }
}

// 切换云端模型
async function switchCloudModel(modelName) {
    try {
        showLoading(true);
        
        const response = await fetch(`/api/models/switch?model_type=cloud&model_name=${modelName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            showNotification(`已切换到云端模型: ${modelName}`, 'success');
            currentCloudModel = modelName;
        } else {
            throw new Error('切换云端模型失败');
        }
    } catch (error) {
        showNotification('切换云端模型失败: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// 测试模型状态
async function testModels() {
    try {
        if (testModelsBtn) {
            testModelsBtn.disabled = true;
            testModelsBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> 检测中...';
        }
        
        // 重置状态
        if (localModelStatus) {
            localModelStatus.textContent = '检测中...';
            localModelStatus.className = 'status-badge checking';
        }
        if (cloudModelStatus) {
            cloudModelStatus.textContent = '检测中...';
            cloudModelStatus.className = 'status-badge checking';
        }
        
        const response = await fetch('/api/models/status');
        if (response.ok) {
            const result = await response.json();
            
            // 更新本地模型状态
            if (localModelStatus) {
                if (result.local_model.available) {
                    localModelStatus.textContent = '可用';
                    localModelStatus.className = 'status-badge connected';
                } else {
                    localModelStatus.textContent = '不可用';
                    localModelStatus.className = 'status-badge failed';
                }
            }
            
            // 更新云端模型状态
            if (cloudModelStatus) {
                if (result.cloud_model.status === 'available') {
                    cloudModelStatus.textContent = '可用';
                    cloudModelStatus.className = 'status-badge connected';
                } else {
                    cloudModelStatus.textContent = '不可用';
                    cloudModelStatus.className = 'status-badge failed';
                }
            }
            
            showNotification('模型状态已更新', 'success');
        } else {
            throw new Error('获取模型状态失败');
        }
    } catch (error) {
        showNotification('测试模型失败: ' + error.message, 'error');
        
        // 设置失败状态
        if (localModelStatus) {
            localModelStatus.textContent = '检测失败';
            localModelStatus.className = 'status-badge failed';
        }
        if (cloudModelStatus) {
            cloudModelStatus.textContent = '检测失败';
            cloudModelStatus.className = 'status-badge failed';
        }
    } finally {
        if (testModelsBtn) {
            testModelsBtn.disabled = false;
            testModelsBtn.innerHTML = '<i class="fas fa-sync-alt"></i> 测试模型';
        }
    }
}

// 切换数据库
async function switchDatabase(target) {
    try {
        showLoading(true);
        
        const response = await fetch('/api/switch_db', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ target: target })
        });

        if (response.ok) {
            const result = await response.json();
            showNotification(`已切换到${target === 'hospital' ? '医疗' : '仓储'}数据库`, 'success');
            
            // 清空聊天记录
            clearChat();
        } else {
            throw new Error('切换数据库失败');
        }
    } catch (error) {
        showNotification('切换数据库失败: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// 发送消息
async function sendMessage() {
    const question = questionInput.value.trim();
    if (!question) return;

    // 添加用户消息
    addMessage(question, 'user');
    
    // 清空输入框
    questionInput.value = '';
    
    // 禁用发送按钮
    sendBtn.disabled = true;
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUser,
                question: question,
                model_type: currentModelType,
                cloud_model: currentModelType === 'cloud' ? currentCloudModel : undefined
            })
        });

        if (response.ok) {
            const result = await response.json();
            addMessage(result.answer, 'assistant', result.meta);
        } else {
            const errorData = await response.json();
            addMessage('抱歉，处理您的请求时出现错误: ' + errorData.detail, 'assistant', { error: true });
        }
    } catch (error) {
        addMessage('网络错误，请检查连接后重试', 'assistant', { error: true });
    } finally {
        showLoading(false);
        sendBtn.disabled = false;
        questionInput.focus();
    }
}

// 添加消息到聊天区域
function addMessage(content, type, meta = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;
    
    messageDiv.appendChild(messageContent);
    
    // 添加元数据
    if (meta && Object.keys(meta).length > 0) {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        
        if (meta.error) {
            metaDiv.innerHTML = '<strong>⚠️ 错误</strong>';
        } else if (meta.sql) {
            metaDiv.innerHTML = `
                <strong>🔍 查询信息</strong><br>
                SQL: <code>${meta.sql}</code><br>
                角色: ${meta.role} | 数据库: ${meta.database}<br>
                结果数量: ${meta.result_count || 0}
            `;
        } else if (meta.tool) {
            metaDiv.innerHTML = `<strong>🌤️ 天气工具</strong> | 数据源: ${meta.data_source}`;
        } else if (meta.model) {
            metaDiv.innerHTML = `<strong>🤖 ${meta.model}</strong> | 类型: ${meta.type}`;
        }
        
        messageDiv.appendChild(metaDiv);
    }
    
    chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 测试数据库连接
async function testDatabaseConnections() {
    try {
        testConnectionBtn.disabled = true;
        testConnectionBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> 检测中...';
        
        // 重置状态
        hospitalStatus.textContent = '检测中...';
        hospitalStatus.className = 'status-badge checking';
        warehouseStatus.textContent = '检测中...';
        warehouseStatus.className = 'status-badge checking';
        
        const response = await fetch('/api/test_db_connections');
        if (response.ok) {
            const result = await response.json();
            
            // 更新医疗数据库状态
            if (result.hospital.status === 'connected') {
                hospitalStatus.textContent = '已连接';
                hospitalStatus.className = 'status-badge connected';
            } else {
                hospitalStatus.textContent = '连接失败';
                hospitalStatus.className = 'status-badge failed';
            }
            
            // 更新仓储数据库状态
            if (result.warehouse.status === 'connected') {
                warehouseStatus.textContent = '已连接';
                warehouseStatus.className = 'status-badge connected';
            } else {
                warehouseStatus.textContent = '连接失败';
                warehouseStatus.className = 'status-badge failed';
            }
            
            showNotification('数据库连接状态已更新', 'success');
        } else {
            throw new Error('获取连接状态失败');
        }
    } catch (error) {
        showNotification('测试连接失败: ' + error.message, 'error');
        
        // 设置失败状态
        hospitalStatus.textContent = '检测失败';
        hospitalStatus.className = 'status-badge failed';
        warehouseStatus.textContent = '检测失败';
        warehouseStatus.className = 'status-badge failed';
    } finally {
        testConnectionBtn.disabled = false;
        testConnectionBtn.innerHTML = '<i class="fas fa-sync-alt"></i> 测试连接';
    }
}

// 清空聊天记录
function clearChat() {
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <div class="message-content">
                <h3>🔄 已切换到${currentDatabase === 'hospital' ? '医疗' : '仓储'}数据库</h3>
                <p>现在您可以查询${currentDatabase === 'hospital' ? '医疗' : '仓储'}相关的信息了！</p>
                <p>请选择您的角色并开始提问。</p>
            </div>
        </div>
    `;
}

// 显示/隐藏加载指示器
function showLoading(show) {
    loading.style.display = show ? 'flex' : 'none';
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // 添加样式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1001;
        animation: slideInRight 0.3s ease;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    // 根据类型设置背景色
    if (type === 'success') {
        notification.style.background = '#48bb78';
    } else if (type === 'error') {
        notification.style.background = '#f56565';
    } else {
        notification.style.background = '#4299e1';
    }
    
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .fa-spin {
        animation: spin 1s linear infinite;
    }
`;
document.head.appendChild(style);
