<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const s = ref({})
onMounted(async () => { s.value = await getJSON('/api/settings') })
</script>
<template><div class="page"><h1>遮盖力参数</h1><p>每升可刷 {{ s.coverage }} m² · 默认 {{ s.coats }} 遍 · 默认损耗 {{ s.waste_pct ?? 0 }}%（上限 {{ s.waste_max_pct ?? 20 }}%）</p></div></template>
