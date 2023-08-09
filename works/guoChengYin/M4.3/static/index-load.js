function valueToColor(value) {
  switch (true) {
    case (value < 1200):
      color = "gray";     // 灰色
      break;
    case (value < 1400):
      color = "green";    // 绿色
      break;
    case (value < 1600):
      color = "cyan";     // 青色
      break;
    case (value < 1900):
      color = "blue";     // 蓝色
      break;
    case (value < 2100):
      color = "purple";   // 紫色
      break;
    case (value < 2300):
      color = "orange";   // 橙色
      break;
    case (value < 3000)://红色
      color = "red";
      break;
    default:
      color = "#cc0033"//新增黑色
      break;
  }
  return color
  // 红色
}


function requestInfo() {
  let handle = document.getElementsByName('handle')[0].value
  var xhr = new XMLHttpRequest()
  xhr.open('GET', "requestUserInfo?handle=" + handle, false);
  try {
    xhr.send()
  } catch (e) {
    console.log(e)
  }
  console.log(xhr.readyState)
  if (xhr.status == "200" || xhr.status == "304") {
    responseData = JSON.parse(xhr.response)
    console.log(responseData)
    document.getElementById("firstLetter").textContent = responseData["handle"].substring(0, 1)
    document.getElementById("partLetter").textContent = responseData["handle"].substring(1)
    document.getElementById("rating").textContent = responseData["rating"]
    document.getElementById("firstLetter").style.color = valueToColor(responseData["rating"])
    document.getElementById("partLetter").style.color = valueToColor(responseData["rating"])
    if (responseData["rating"] > 3000) {
      document.getElementById("firstLetter").style.color = 'black'
    }
    const tableThead = document.querySelector("#table1 thead");
    if (responseData["rating"] != "暂无") {
      tableThead.style.display = ""
    } else {
      tableThead.style.display = "none"
    }
    renderTable(responseData)
    //客户端未连接网络等情况
  } else if (xhr.status == 0) {
    alert("建立网络连接失败")
  } else {
    alert(xhr.responseText)
  }
}

const UpdatedAts = []
const ratings = []

function renderTable(data) {
  const tableBody = document.querySelector("#table1 tbody");
  tableBody.innerHTML = "";
  rating_hisyory = data["rating_history"]
  rating_hisyory.forEach(function (v) {
      const row = document.createElement("tr");
      const dateCell = document.createElement("td")
      const contestNameCell = document.createElement("td");
      const ratingCell = document.createElement("td");
      const rankCell = document.createElement("td")
      dateCell.textContent = v["ratingUpdatedAt"]

      contestNameCell.textContent = v["contestName"].toString().trim()
      ratingCell.textContent = v["oldRating"] + "—>" + v["newRating"]
      rankCell.textContent = v["rank"]
      row.appendChild(dateCell)
      row.appendChild(contestNameCell)
      row.appendChild(rankCell)
      row.appendChild(ratingCell)
      tableBody.appendChild(row)
      UpdatedAts.push(v["ratingUpdatedAt"].substring(0, 10))
      ratings.push(v["newRating"])
    }
  )
  console.log(Math.min(...ratings) - Math.min(...ratings) % 100)
  option.yAxis.min = Math.min(...ratings) - Math.min(...ratings) % 100
  option.yAxis.max = Math.max(...ratings)
  myChart.setOption(option);
  UpdatedAts.length = 0
  ratings.length = 0
}
