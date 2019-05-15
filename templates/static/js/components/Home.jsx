import React, { Component } from 'react';
import axios from 'axios';
import { Chart } from "react-google-charts";

const labels = [
    'Days',
    'Atlanta Hawks', 'Boston Celtics', 'Cleveland Cavaliers', 
    'New Orleans Pelicans', 'Chicago Bulls', 'Dallas Mavericks', 
    'Denver Nuggets', 'Golden State Warriors', 'Houston Rockets', 
    'Los Angeles Clippers', 'Los Angeles Lakers', 'Miami Heat', 
    'Milwaukee Bucks', 'Minnesota Timberwolves', 'Brooklyn Nets', 
    'New York Knicks', 'Orlando Magic', 'Indiana Pacers', 'Philadelphia 76ers', 
    'Phoenix Suns', 'Portland Trail Blazers', 'Sacramento Kings', 
    'San Antonio Spurs', 'Oklahoma City Thunder', 'Toronto Raptors', 
    'Utah Jazz', 'Memphis Grizzlies', 'Washington Wizards', 'Detroit Pistons', 
    'Charlotte Hornets'
]

export default class Home extends Component {
    constructor () {
        super()
        this.state = {
            predictions_posts: [],
            actual_posts:[],
            options: {
                title: 'NBA 2018-19 SEASON PREDICTIONS',
                hAxis: {
                    title: 'Win / Loss ratio (%)'
                },
                vAxis: {
                    title: 'Days'
                },
                legend: { 
                    position: 'bottom',
                    maxlines: 10
                }
            },
            predictions_is_loaded: false,
            actual_is_loaded: false
        }

        this.displayPredictions = this.displayPredictions.bind(this)
        this.displayActual = this.displayActual.bind(this)
    }

    displayPredictions() {
        this.setState({
            predictions_is_loaded: !this.state.predictions_is_loaded,
            actual_is_loaded: false
        })
    }

    displayActual() {

        this.setState({
            actual_is_loaded: !this.state.actual_is_loaded,
            predictions_is_loaded: false
        })
    }

    componentDidMount() {
        axios.get('/predictions')
        .then(response => {
            let array_of_results = response.data;
            let matrix = [];
            matrix.push(labels);
            array_of_results.forEach(function(entry) {
                let date = JSON.stringify(entry[0]);
                let year = parseInt(date.substring(1,5));
                let month = parseInt(date.substring(6,8));
                let day = parseInt(date.substring(9,11));
                entry[0] = new Date(year, month, day);
                // entry[1] = parseInt(entry[1]);
                matrix.push(entry)
            })
            // console.log(matrix)
            this.state.predictions_posts = matrix;
        })
    
        axios.get('/actual')
        .then(response => {
            let array_of_results = response.data;
            let matrix = [];
            matrix.push(labels);
            array_of_results.forEach(function(entry) {
                let date = JSON.stringify(entry[0]);
                let year = parseInt(date.substring(1,5));
                let month = parseInt(date.substring(6,8));
                let day = parseInt(date.substring(9,11));
                entry[0] = new Date(year, month, day);
                // entry[1] = parseInt(entry[1]);
                matrix.push(entry)
            })
            // console.log(matrix)
            this.state.actual_posts = matrix;
        })
    }

    render() {
        let predictions_graph = null;
        if ( this.state.predictions_is_loaded ) {
            predictions_graph = (
                <Chart
                    width={'100%'}
                    height={'100%'}
                    chartType="Line"
                    loader={<div>Loading Chart</div>}
                    data={this.state.predictions_posts}
                    options={this.state.options}
                />
            )
        }

        let actual_graph = null;
        if ( this.state.actual_is_loaded ) {
            actual_graph = (
                <Chart
                    width={'100%'}
                    height={'100%'}
                    chartType="Line"
                    loader={<div>Loading Chart</div>}
                    data={this.state.actual_posts}
                    options={this.state.options}
                />
            )
        }
        return (
            <div>
                <div class="container header">
                    <img src='public/images/logo.png'/>
                    <h1 class="display-4"> Match Outcome Predictor</h1>
                </div>
                <div class="container links">
                    <p>
                        <a href="https://www.linkedin.com/in/harrison-chun-b83939163/" target="_blank" class="text-primary">Developer </a>
                        |
                        <a href="https://github.com/harrisonwjs/NBA-Predictor" target="_blank" class="text-primary"> Github</a>
                    </p>
                </div>
                <div class="container description">
                    <p>This website predicts the match outcomes of the latest NBA season<b>(2018-19)</b> with <span class="text-success">63-67% accuracy</span>.</p>
                    <p>Each team's win ratios are calculated from all 1230 games and their changes are visualized by a graph of each game day.</p>
                    <p><u>Predictions</u> shows the predicted outcomes and <u>Real</u> show the actual outcomes.</p>
                    <p>The graphs are generated with <a href="https://developers.google.com/chart/" target="_blank" class="text-danger">Google Charts</a></p>
                </div>
                <div class="container buttons">
                    <div class="test">
                        <button className="button" onClick={this.displayPredictions} type="button" class="btn btn-primary">Predictions</button>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        <button className="button" onClick={this.displayActual} type="button" class="btn btn-primary">Real</button>
                    </div>
                </div>
                <div class="container graph">
                    {predictions_graph}
                    {actual_graph}
                </div>
            </div>
        )
    }
}