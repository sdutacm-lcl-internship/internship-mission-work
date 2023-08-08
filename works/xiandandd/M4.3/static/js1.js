new Vue({
    el: '#app',
    data: {
        name: '',
        handle: '',
        contents: [],
        rating: 0,
        times: [],
        ratings: [],
        names: [],
        olds: [],
    },
    methods: {
        add() {
            var my = document.getElementById("yyy");
            var ms = document.getElementById("xxx");
            my.style.display = "none";
            ms.style.display = "none";
            var f = document.getElementById('ratingchart');
            f.style.display = "none";
            this.contents = [];
            this.names = [];
            this.ratings = [];
            this.times = [];
            this.handle = '';
            this.olds = [];
            if (this.name === "") {
                alert("输入不能为空");
                return;
            }
            let dataToSend1 = {
                handle: this.name
            };
            let dataToSend2 = {
                handles: this.name
            };

            let url2 = '/getUserRatings?' + "handle=" + this.name;
            let url1 = '/batchGetUserInfo?' + "handles=" + this.name;
            let num1, num2;
            axios.get(url1)
                .then(response => {
                        num1 = response.status;
                        return response.data;
                    }
                )
                .then(data => {
                    data1 = data;
                    return axios.get(url2)
                })
                .then(response => {
                    num2 = response.status;
                    return response.data;
                })
                .then(data => {
                    data2 = data;
                    //处理数据
                    for (var i = 0; i < data2.length; i++) {
                        this.contents.push({
                            'ratingUpdatedAt': data2[i]["ratingUpdatedAt"],
                            'contestName': data2[i]["contestName"],
                            'rank': data2[i]["rank"],
                            'oldRating': data2[i]["oldRating"],
                            'newRating': data2[i]["newRating"],
                        });
                        this.times.push(data2[i]["ratingUpdatedAt"]);
                        this.ratings.push(data2[i]["newRating"]);
                        this.names.push(data2[i]["contestName"]);
                        this.olds.push(data2[i]["oldRating"]);
                    }

                    if (data2.length === 0) {
                        this.handle = data1[0]["result"]["handle"];
                        this.rating = 0;
                        let textContent = this.handle;
                        let element = document.getElementById("handle");
                        element.innerHTML = textContent;
                        element.style.color = "black";
                        my.style.display = "block";
                    } else {
                        this.handle = data1[0]["result"]["handle"] + "(" + data1[0]["result"]["rank"] + ')';
                        this.rating = data1[0]["result"]["rating"];
                        my.style.display = "block";
                        ms.style.display = "block";
                        f.style.display = "block";
                        this.addchart()
                    }
                    return;
                })
                .catch(error => {
                        if (error.response && error.response.status) {
                            if (error.response.status === 404) {
                                alert("查无此人");
                            } else {
                                alert("出错了！ 状态码: " + error.response.status);
                            }
                        } else {
                            alert("出错了！ ");
                        }
                    });
        },
        addchart() {
            var rating = this.rating;
            var element = document.getElementById("handle");
            var s = '';
            if (rating >= 0 && rating < 1200) {
                s = '#808080'; // 灰色背景
            } else if (rating >= 1200 && rating < 1400) {
                s = '#008000'; // 绿色背景
            } else if (rating >= 1400 && rating < 1600) {
                s = '#03a89e'; // 浅绿色背景
            } else if (rating >= 1600 && rating < 1900) {
                s = '#0000ff'; // 蓝色背景
            } else if (rating >= 1900 && rating < 2100) {
                s = '#a0a'; // 紫色背景
            } else if (rating >= 2100 && rating < 2300) {
                s = '#ff8c00'; // 橙色背景
            } else if (rating >= 2300 && rating < 2400) {
                s = '#ff8c00'; // 黄色背景
            } else if (rating >= 2400 && rating < 2600) {
                s = '#ff0000'; // 红色背景
            } else if (rating >= 2600 && rating <= 3000) {
                s = '#ff0000'; // 深红色背景
            } else if (rating > 3000) {
                s = '#ff0000';
            } else {
                s = 'rgb(127,0,0)'; //
            }
            if (rating > 3000) {
                let textContent = this.handle;
                let newHTML = "<span style='color: black'>" + textContent.charAt(0) + "</span>";
                newHTML += "<span style='color: #ff0000'>" + textContent.slice(1) + "</span>";
                element.innerHTML = newHTML;
            } else {
                let textContent = this.handle;
                element.innerHTML = textContent;
                element.style.color = s;
            }
            // 准备数据
            var chart = echarts.init(document.getElementById('ratingchart'));
            var p = this.times;
            var pp = this.ratings;
            var old = this.olds;

            var maxx = 0;
            // 获取rating数据中的最大值
            for (var k = 0; k < pp.length; k++) {
                if (maxx < pp[k]) {
                    maxx = pp[k];
                }
            }
            maxx = maxx + 500;
            var ppp = this.names;
            let pppp = p.map(str => str.slice(0, 10));
            var uu = [];
            for (var u = 0; u < pppp.length; u++) {
                uu[u] = [];
                uu[u].push(new Date(pppp[u]));
                uu[u].push(pp[u]);
            }
            // 配置项
            var option = {
                title: {
                    text: '比赛成绩分布',
                    subtext: ''
                },
                tooltip: {
                    formatter: function (params) {
                        var data = params.data;  // 获取当前气泡的数据
                        let index = params.dataIndex;//获取当前气泡的索引

                        var x = p[index];
                        var y = pp[index];
                        var z = ppp[index];
                        var q = pp[index] - old[index];//变化值
                        if (q >= 0) {
                            return '比赛时间：' + x + '<br>'
                                + 'rating：' + y + '(+' + q + ')' + '<br>'
                                + '比赛名称:' + z;
                        } else {
                            return '比赛时间：' + x + '<br>'
                                + 'rating：' + y + '(' + q + ')' + '<br>'
                                + '比赛名称:' + z;
                        }

                    }
                },
                toolbox: {
                    show: true,
                    feature: {
                        saveAsImage: {}
                    }
                },
                xAxis: {
                    type: 'time',
                },
                yAxis: {
                    type: 'value',
                    max: maxx,
                },
                // 省略其余的配置

                series: [
                    {
                        type: 'line',
                        data: uu
                    },
                    // {
                    //     name: 'rating',
                    //     type: 'line',
                    //     smooth: true,
                    //     data: this.ratings
                    // },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '0'},
                                    {yAxis: '1200'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgb(204,204,204)' // 第一个区域的颜色为橙色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '1200'},
                                    {yAxis: '1400'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgb(119,255,119)' // 第二个区域的颜色为绿色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '1400'},
                                    {yAxis: '1600'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(119,221,187)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '1600'},
                                    {yAxis: '1900'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(170,170,255)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '1900'},
                                    {yAxis: '2100'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(255,136,255)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '2100'},
                                    {yAxis: '2300'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(255,204,136)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '2300'},
                                    {yAxis: '2400'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(255,187,85)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '2400'},
                                    {yAxis: '2600'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(255,119,119)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '2600'},
                                    {yAxis: '3000'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(255,51,51)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '3000'},
                                    {yAxis: '10000'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(170,0,0)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                ]

            };

            // 应用配置
            chart.setOption(option);
        }
    }
});
