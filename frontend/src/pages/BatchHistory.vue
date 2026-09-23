<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const cur = ref(null)
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
const open = async (id) => { cur.value = await getJSON(`/api/history/${id}`) }
</script>
<template><div class="page"><h1>估算记录</h1>
<table><tr v-for="h in items" :key="h.id" class="pick" @click="open(h.id)"><td>#{{ h.id }}</td><td>{{ h.created_at }}</td></tr></table>
<p v-if="cur">#{{ cur.id }} 基础 {{ cur.result.base_liters ?? cur.result.liters }} 升 · 损耗 {{ cur.result.waste_pct ?? 0 }}% · 应付 {{ cur.result.payable_liters ?? cur.result.liters }} 升</p>
</div></template>
