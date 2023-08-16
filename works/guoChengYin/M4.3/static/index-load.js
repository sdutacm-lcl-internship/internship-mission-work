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

let max = -1
let min = 100000
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
    if(v["newRating"]>max){
      max=v["newRating"]
    }
    if(v["newRating"]<min){
      min = v["newRating"]
    }
      ratings.push([v["ratingUpdatedAt"].substring(0, 10),v["newRating"]])
    }
  )

  option.yAxis.min =min- min% 100
  option.yAxis.max = max
  console.log(max)
  option.xAxis.data=ratings
  myChart.setOption(option);
  ratings.length = 0
  max=-1
  min=100000
}

