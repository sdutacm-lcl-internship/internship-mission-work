<script setup>
import { ref, computed } from 'vue'
import { queryUser, queryContests } from '@/api/user.js'

const handle = ref(""); // 存储输入的 handle
const userResult = ref(null); // 存储查询到的用户信息
const contestResult = ref([]); // 存储查询到的比赛信息
const isContestQueried = ref(false); // 标志位，是否已经查询过比赛信息

// 分页相关状态
const currentPage = ref(1); // 当前页码
const pageSize = ref(10); // 每页显示的记录数
const pagedContestResult = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return contestResult.value.slice(start, end);
});

const query = async (users) => {
  // 将拿到的字符串分割成字符串数组，并去除多余空格
  const list = users.split(",").map(item => item.trim());
  const responseUser = await queryUser(list);
  const responseContests = await queryContests(list);
  console.log(responseUser);
  console.log(responseContests);
  userResult.value = responseUser.data.data;
  contestResult.value = responseContests.data.data; // 假设 contests 数据在接口返回中
  isContestQueried.value = true; // 查询完成后设置为 true
  currentPage.value = 1; // 重置分页页码
};
</script>

<template>
  <div>
    <el-container class="app-container">
      <el-header>
        <h1>Codeforces 个人信息查询</h1>
      </el-header>
      <el-main>
        <!-- 用户信息输入 -->
        <el-row justify="center" class="top-input">
          <el-input
            v-model="handle"
            placeholder="请输入handle"
            class="input-box"
          />
          <el-button type="primary" @click="query(handle)" class="fetch-btn">
            一键查询
          </el-button>
        </el-row>

        <!-- 用户信息结果展示 -->
        <el-row justify="center" class="result-container">
          <div v-if="userResult && userResult.length > 0" class="result">
            <div v-for="(user, index) in userResult" :key="index">
              <div class="handle">Handle: {{ user.handle }}</div>
              <div class="rank">Rank: {{ user.rank }}</div>
              <div class="rating">Rating: {{ user.rating }}</div>
            </div>
          </div>
          <div v-else-if="userResult && userResult.length === 0" class="no-result">
            <p>未找到相关用户信息。</p>
          </div>
        </el-row>

        <!-- 比赛信息表格 -->
        <el-row justify="center" class="contest-container">
          <template v-if="isContestQueried">
            <el-table
              v-if="pagedContestResult && pagedContestResult.length > 0"
              :data="pagedContestResult"
              style="width: 100%; margin-top: 20px;"
            >
              <el-table-column prop="contestId" label="比赛ID" width="120" />
              <el-table-column prop="contestName" label="比赛名称" />
              <el-table-column prop="rank" label="选手排名" width="120" />
              <el-table-column prop="oldRating" label="比赛前Rating" width="150" />
              <el-table-column prop="newRating" label="比赛后Rating" width="150" />
              <el-table-column
                prop="ratingUpdatedAt"
                label="比赛时间"
                width="180"
                v-slot="{ row }"
              >
                {{ new Date(row.ratingUpdatedAt).toLocaleString() }}
              </el-table-column>
            </el-table>
            <div v-else class="no-result">
              <p>未找到比赛信息。</p>
            </div>
            <!-- 分页组件 -->
            <el-pagination
              v-if="contestResult && contestResult.length > 0"
              v-model:currentPage="currentPage"
              :page-size="pageSize"
              :total="contestResult.length"
              layout="prev, pager, next"
              class="pagination"
              style="margin-top: 20px;"
            />
          </template>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>
.app-container {
  text-align: center;
  padding: 20px;
}

h1 {
  color: #000;
  font-size: 36px;
  margin: 20px 0;
}

.top-input {
  margin: 20px 0;
}

.input-box {
  width: 300px;
  margin-right: 10px;
}

.fetch-btn {
  width: 120px;
}

.result-container {
  margin-top: 20px;
}

.result div {
  font-size: 20px;
  margin: 10px 0;
}

.contest-container {
  margin-top: 20px;
}

.no-result {
  font-size: 18px;
  color: gray;
  text-align: center;
}

.pagination {
  display: flex;
  justify-content: center;
}
</style>
