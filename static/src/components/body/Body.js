import React, { Component } from 'react'
import { Row, Col, Grid } from 'react-bootstrap'
import Login from './Login'
import Register from './Register'
import UpdateAvailability from './UpdateAvailability'
import { connect } from 'react-redux'
import { Route } from 'react-router-dom'

class Body extends Component {

  constructor(props) {
    super(props);
    this.state = {
      
    };
  }
  render() {
    return (
      <div>
        <Grid>
          <Row>
              {/* body part */}
                <Route exact path='/' render={()=>{
                  return(
                    <div>
                      {Login}
                      {Register}
                      {UpdateAvailability}
                    </div>
                  )
                }} />
				<Route path='/Login' component={Login}/>
                <Route path='/Register' component={Register}/>
                <Route path='/UpdateAvailability' component={UpdateAvailability}/>
          </Row>
        </Grid>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    user: state.login.user
  }
}

Body = connect(
  mapStateToProps,
)(Body);

export default Body;
