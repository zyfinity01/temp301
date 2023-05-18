const csv = require('csv-parser');
const fs = require('fs');

class Watershed {
    constructor(filename) {
        this.filename = filename;
    }

    readCSV() {
        const results = [];
        fs.createReadStream(this.filename)
            .pipe(csv({}))
            .on('data', (data) => {
                if (data.Maxim_DS3231_Temp != 'nan') {
                    data.Maxim_DS3231_Temp = +data.Maxim_DS3231_Temp;
                }
                if (data.TBRain_5Min != 'nan') {
                    data.TBRain_5Min = +data.TBRain_5Min;
                }
                results.push(data);
            })
            .on('end', () => {
                console.log(results);
            });
        return results;
    }
}

module.exports = {
    Watershed
}

const data = new Watershed("../VUW_Test_TimeSeriesResults.csv");
console.log(data.readCSV());
