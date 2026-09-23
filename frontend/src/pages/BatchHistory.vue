<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const qid = ref('')
const one = ref(null)
const err = ref('')
const load = async () => { items.value = (await getJSON('/api/history')).items }
onMounted(load)
const fetchOne = async () => {
  err.value = ''; one.value = null
  try { one.value = await getJSON(`/api/history/${qid.value}`) }
  catch (e) { err.value = e.message }
}
</script>
<template><div class="page"><h1>估算记录</h1>
<table>
  <tr><th>编号</th><th>时间</th><th>房间</th></tr>
  <tr v-for="h in items" :key="h.id">
    <td><a href="#" @click.prevent="qid = h.id; fetchOne()">#{{ h.id }}</a></td>
    <td>{{ h.created_at }}</td><td>{{ h.room_id }}</td>
  </tr>
</table>
<div v-if="one">
  <h2>#{{ one.id }} 钉选结果</h2>
  <p>基础升数 {{ one.liters }} L · 损耗 {{ one.waste_pct }}% ·
     应付升数 <span class="hero-num">{{ one.chargeable_liters }} L</span></p>
</div>
<p class="err" v-if="err">{{ err }}</p>
</div></template>
