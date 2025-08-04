<template>
    <div class="container">
        <h1>查询选手</h1>

        <div class="search">
            <input v-model="input" placeholder="Enter handle" @keyup.enter="handleSearch" />
            <button @click="handleSearch">查询</button>
        </div>

        <div v-if="loading">查询中...</div>
        <div v-if="error" class="error">{{ error }}</div>

        <div v-for="result in results" :key="result.handle" class="card">
            <div v-if="result.user && result.user.success">
                <h3>查询结果</h3>
                <p><strong>Handle:</strong> {{ result.user.result.handle }} ({{ result.user.result.rank ?? '无段位' }})</p>
                <p><strong>Rating:</strong> {{ result.user.result.rating ?? '无记录' }}</p>
                <graph :ratings="result.ratings" />

            </div>
            <div v-else>
                <h3>查询结果</h3>
                <p>{{ result.handle }}</p>
                <p>查无此人</p>
            </div>
        </div>
    </div>
</template>

<script setup>
    import graph from './graph.vue'
    import { ref } from 'vue'

    const input = ref('')
    const loading = ref(false)
    const error = ref('')
    const results = ref([])

    const handleSearch = async () => {
        results.value = []
        error.value = ''

        const handles = input.value
            .split(',')
            .map(h => h.trim())
            .filter(Boolean)

        if (handles.length === 0) {
            error.value = '请输入有效的 handle'
            setTimeout(() => {
                error.value = ''
            }, 2500);
            return
        }

        loading.value = true

        try {
            const requests = handles.map(async (handle) => {
                const userInfo = await fetch(`/batchGetUserInfo?handles=${handle}`).then(res => res.json())
                const userRatings = await fetch(`/getUserRatings?handle=${handle}`).then(res => res.json())

                return {
                    handle,
                    user: userInfo?.[0] ?? null,
                    ratings: userRatings
                }
            })
            results.value = await Promise.all(requests)
        } catch (err) {
            error.value = '查询失败'
        } finally {
            loading.value = false
        }
    }
</script>

<style scoped>
    .container {
        margin: 40px;
        text-align: center;
    }

    input {
        padding: 3px;
    }

    button {
        padding: 2px 12px;
        margin: 5px;
    }

    .search {
        margin-bottom: 20px;
    }

    .error {
        color: red;
        margin: 10px;
    }

    .card {
        margin: 50px auto;
        width: 80%;
    }

</style>
