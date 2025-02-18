<template>
  <div class="process-manager">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>进程管理器</span>
          <el-button type="primary" @click="refreshProcesses">刷新</el-button>
        </div>
      </template>
      <el-table :data="processes" style="width: 100%">
        <el-table-column prop="pid" label="PID" />
        <el-table-column prop="name" label="进程名" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const processes = ref([])

const refreshProcesses = async () => {
  try {
    const response = await axios.get('/api/processes')
    if (response.data.code === 200) {
      processes.value = response.data.data
    }
  } catch (error) {
    console.error('获取进程列表失败:', error)
  }
}

onMounted(() => {
  refreshProcesses()
})
</script>