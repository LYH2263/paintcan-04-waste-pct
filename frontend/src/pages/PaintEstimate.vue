<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const room_id = ref(1)
const waste = ref('')
const out = ref(null)
const err = ref('')
const run = async () => {
  err.value = ''; out.value = null
  try {
    out.value = await postJSON('/api/estimate', {
      room_id: room_id.value, persist: true,
      waste_pct: waste.value === '' ? null : +waste.value,
    })
  } catch (e) { err.value = String(e) }
}
</script>
<template><div class="page"><h1>估漆工作台</h1>
<label>房间ID <input v-model.number="room_id" /></label>
<label>损耗% <input v-model="waste" placeholder="默认" /></label>
<button @click="run">估算</button>
<p v-if="err" class="err">{{ err }}</p>
<p v-if="out">净 {{ out.net_m2 }} m² · 基础 {{ out.base_liters }} 升 · 损耗 {{ out.waste_pct }}% · 应付 {{ out.payable_liters }} 升 · {{ out.coats }} 遍</p></div></template>
