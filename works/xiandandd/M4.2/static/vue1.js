
new Vue({
    el: '#app',
    data: {
        name: '',
        // content: '',
        handle: '',
        rating: '',
        td: [],
        contents:[],
    },
    methods: {
        add() {
            this.td=[];
            this.contents=[];
            const newContent = {
            id: Date.now(),
            content: ''
          };
            let dataToSend1 = {
                handle: this.name
            };
            let dataToSend2 = {
                handles: this.name
            };
            let datas;
            let queryString1 = Object.keys(dataToSend1).map(key => key + '=' + dataToSend1[key]).join('&');
            let url1 = 'http://127.0.0.1:2333/getUserRatings?' + queryString1;
            let num1, num2;
            axios.get(url1)
                .then(response => {
                        num1 = response.status;
                        if (num1 === 200) {
                            return response.data;
                        }
                    }
                )
                .then(data => {
                    datas=data;
                        console.log(data);
                        if (data.length === 0 && num1 === 200) {
                            this.handle = this.name;
                            newContent.content = '<div align="center">\n' +
                                    '    <h2>查询结果</h2>\n' +
                                '        <p id="handle">'+this.handle+'</p>\n' +
                                '<p>比赛记录为空</p>'+'</div>';
                            this.contents.push(newContent);
                        }
                        else if (num1 == 200) {
                                let queryString2 = Object.keys(dataToSend2).map(key => key + '=' + dataToSend2[key]).join('&');
                                let url2 = 'http://127.0.0.1:2333/batchGetUserInfo?' + queryString2;
                                return axios.get(url2);
                        }
                        else if (num1===404){
                            newContent.content = '<div align="center">\n' +
                                    '    <h2>查询结果</h2>\n' +
                                '        <p id="handle">'+'查无此人'+'</p>\n'
                                +'</div>';
                            this.contents.push(newContent);
                        }
                        else{
                            newContent.content = '<div align="center">\n' +
                                    '    <h2>查询结果</h2>\n' +
                                '        <p id="handle">'+'服务异常，请稍后再试'+'</p>\n'
                                +'</div>';
                            this.contents.push(newContent);
                        }
                })
                .then(response => {
                    console.log("00000")
                    num2 = response.status;

                    return response.data;
                })
                .then(data => {
                    this.handle = data[0]['result']['handle'] + '(' + data[0]['result']['rank'] + ')';
                    this.rating = data[0]['result']['rating'];
                    for (let i = 0; i < datas.length; i++) {
                                this.td.push(
                                    `<tr>
                                    <td>${datas[i]['ratingUpdatedAt']}</td>
                                    <td>${datas[i]['contestName']}</td>
                                    <td>${datas[i]['rank']}</td>
                                    <td>${datas[i]['oldRating']}->${datas[i]['newRating']}</td>
                                    </tr>`
                                );
                            }

                                newContent.content = '<div align="center">\n' +
                                    '    <h2>查询结果</h2>\n' +
                                    '    <div align="center">\n' +
                                    '        <p id="handle">'+this.handle+'</p>\n' +
                                    '        <span style="font-size: 25px">rating:</span>\n' +
                                    '        <p id="rating">'+this.rating+'</p>\n' +
                                    '    </div>\n' +
                                    '</div>\n' +
                                    '<div align="center" style="margin-top:50px">\n' +
                                    '    <p style="align-content: center;color: darkgrey">rating history</p>\n' +
                                    '    <table style="border: 1px solid black">\n' +
                                    '        <thead>\n' +
                                    '        <tr>\n' +
                                    '            <th>时间</th>\n' +
                                    '            <th>比赛</th>\n' +
                                    '            <th>rank</th>\n' +
                                    '            <th>△</th>\n' +
                                    '        </tr>\n' +
                                    '        </thead>\n' +
                                    '        <tbody>\n' + this.td +
                                    '        </tbody>\n' +
                                    '    </table>\n' +
                                    '</div>';
                    this.contents.push(newContent);
                })
                .catch(error => {
                    console.log(error.response.status)
                    if (error.response.status===404){
                            newContent.content = '<div align="center">\n' +
                                    '    <h2>查询结果</h2>\n' +
                                '        <p id="handle">'+'查无此人'+'</p>'
                                +'</div>';
                            this.contents.push(newContent);
                        }
                        else{
                            newContent.content = '<div align="center">\n' +
                                    '    <h2>查询结果</h2>\n' +
                                '        <p id="handle">'+'服务异常，请稍后再试'+'</p>\n'
                                +'</div>';
                            this.contents.push(newContent);
                        }
                });
        }
    }
});
