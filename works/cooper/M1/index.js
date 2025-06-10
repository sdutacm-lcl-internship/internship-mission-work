const axios = require("axios");

const codeforces_baseurl = "https://codeforces.com/api/";

// 封装请求函数
const fetchData = async (methodName, params) => {
  const url =
    codeforces_baseurl + methodName + "?" + new URLSearchParams(params);
  const response = await axios.get(url);
  return response.data;
};

// 查询用户信息
const getUserInfo = async (handle) => {
  const params = {
    handles: handle,
  };
  return await fetchData("user.info", params);
};

// 解析命令行参数
const args = process.argv.slice(2);

// 解析参数
const userInfo = {
  handle: args[0],
};

// 执行查询
if (userInfo.handle) {
  // 特殊情况：缺少运行参数
  getUserInfo(userInfo.handle)
    .then((res) => {
      if(res.status === "OK") {
        const user = res.result[0];
        if (user.rating) {
          userInfo.rating = user.rating;
          userInfo.rank = user.rank;
        }
        console.log(JSON.stringify(userInfo));
      } else {
        throw new Error(res.comment);
      }
    })
    .catch((err) => {
      if(err.response) {
        console.log("no such handle");
      } else {
        console.log("[请求失败] ", err.message);
      }
    });
} else {
  console.log("[缺少参数]");
}
