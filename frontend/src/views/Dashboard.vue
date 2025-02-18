<template>
  <div class="dashboard">
    <!-- 系统状态卡片 -->
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">CPU 使用率</div>
          </template>
          <el-progress 
            type="dashboard" 
            :percentage="serverStatus.cpu_usage"
            :color="getStatusColor(serverStatus.cpu_usage)"
          />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">内存使用率</div>
          </template>
          <el-progress 
            type="dashboard" 
            :percentage="serverStatus.memory_usage"
            :color="getStatusColor(serverStatus.memory_usage)"
          />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">磁盘使用率</div>
          </template>
          <el-progress 
            type="dashboard" 
            :percentage="serverStatus.disk_usage"
            :color="getStatusColor(serverStatus.disk_usage)"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统信息卡片 -->
    <el-row :gutter="20" class="mt-4">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">系统信息</div>
          </template>
          <div class="info-list">
            <div class="info-item">
              <span class="label">操作系统：</span>
              <span>{{ systemInfo.os }}</span>
            </div>
            <div class="info-item">
              <span class="label">主机名：</span>
              <span>{{ systemInfo.hostname }}</span>
            </div>
            <div class="info-item">
              <span class="label">运行时间：</span>
              <span>{{ systemInfo.uptime }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">进程概览</div>
          </template>
          <div class="info-list">
            <div class="info-item">
              <span class="label">总进程数：</span>
              <span>{{ processInfo.total }}</span>
            </div>
            <div class="info-item">
              <span class="label">运行中：</span>
              <span>{{ processInfo.running }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const serverStatus = ref({
  cpu_usage: 0,
  memory_usage: 0,
  disk_usage: 0
})

const systemInfo = ref({
  os: '',
  hostname: '',
  uptime: ''
})

const processInfo = ref({
  total: 0,
  running: 0
})

// 获取服务器状态
const fetchServerStatus = async () => {
  try {
    const response = await axios.get('/api/server-status')
    if (response.data.code === 200) {
      serverStatus.value = response.data.data
    } else {
      ElMessage.error(response.data.message || '获取服务器状态失败')
    }
  } catch (error) {
    console.error('获取服务器状态失败:', error)
    ElMessage.error(error.response?.data?.message || '服务器错误')
  }
}

// 获取系统信息
const fetchSystemInfo = async () => {
  try {
    const response = await axios.get('/api/system-info')
    if (response.data.code === 200) {
      systemInfo.value = response.data.data
    }
  } catch (error) {
console.error('获取系统信息失败:', error)
  }
}

// 获取进程信息
const fetchProcessInfo = async () => {
  try {
    const response = await axios.get('/api/process-info')
    if (response.data.code === 200) {
      processInfo.value = response.data.data
    }
  } catch (error) {
    console.error('获取进程信息失败:', error)
  }
}

// 根据使用率返回不同的颜色
const getStatusColor = (percentage) => {
  if (percentage < 60) return '#67C23A'
  if (percentage < 80) return '#E6A23C'
  return '#F56C6C'
}

let timer

onMounted(() => {
  fetchServerStatus()
  fetchSystemInfo()
  fetchProcessInfo()
  // 每5秒更新一次状态
  timer = setInterval(() => {
    fetchServerStatus()
    fetchProcessInfo()
  }, 5000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.mt-4 {
  margin-top: 20px;
}

.card-header {
  font-weight: bold;
}

.info-list {
  padding: 10px;
}

.info-item {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.label {
  font-weight: bold;
  margin-right: 10px;
  min-width: 100px;
}
</style>