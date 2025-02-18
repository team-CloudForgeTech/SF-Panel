<template>
  <div class="file-manager">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>文件管理器</span>
          <el-button type="primary" @click="refreshFiles">刷新</el-button>
        </div>
      </template>
      <el-table :data="files" style="width: 100%">
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="type" label="类型" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const files = ref([])

const refreshFiles = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/files')
    if (response.data.code === 200) {
      files.value = response.data.data
    }
  } catch (error) {
    console.error('获取文件列表失败:', error)
  }
}

onMounted(() => {
  refreshFiles()
})
</script>