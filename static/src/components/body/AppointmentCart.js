import {Component} from "react";
import React from "react";
import {Table, Button, Checkbox, Modal, Input, Popconfirm, message} from 'antd';
import { Alert } from 'react-bootstrap'
import { fetchAPI } from '../utility'
import 'antd/es/table/style/index.css';
import 'antd/es/modal/style/index.css';
import 'antd/es/message/style/index.css';
import 'antd/es/popconfirm/style/css.js';


class AppointmentCart extends Component {
    constructor(props) {
        super(props);
        this.state = { visible: false, 
            length: '', 
            date:'', 
            time:'',
            clinic_id:'',
            //alert notifies if appointment already exists
            alert: false,
            success: false,
            annualAlert: false,
            clinics: [], 
         }
        this.getClinics();
        this.onCheckout = this.onCheckout.bind(this)
        this.TableGenerator = this.TableGenerator.bind(this)
        
    }

    showModal = () => {
        this.setState({
            visible: true,
        });
    }

    handleOk = (e) => {
        this.setState({
            visible: false,
        });
        this.checkout()
    }

    handleCancel = (e) => {
        this.setState({
            visible: false,
            length: '',
            date: '',
            time: '',
        });
    }

    onCheckout(appointment){
        console.log("onCheckout appointment:" + JSON.stringify(appointment));
        if (appointment[0] === 'Checkup'){
            this.setState({length:'20'});
        }
        if (appointment[0] === 'Annual'){
            this.setState({length:'60'});
        }
        this.setState({date: appointment[1], time: appointment[2], clinic_id: appointment[3]}, () => {
            console.log("onCheckout Clinic id is: " + this.state.clinic_id);
        });

        this.showModal()
    }
    
    onRemove(appointment){
        this.setState({
            length: '',
            date: '',
            time: '',
        });
        this.props.removeFromCart(appointment)
    }

    async getClinics(){
        fetchAPI("GET", '/api/clinic/findAll').then(
            response => {
                try{
                    if(response.success){
                        this.setState({
                            clinics: response.clinics
                        });
                        console.log('retrieved clinics')
                    }
                    else {
                        console.log('failed to retrieve clinics')
                    }
                } catch(e) {console.error("Error getting appointments for patient:", e)}
            }
        ).catch((e)=>console.error("Error getting appointments for patient:", e))
    }

    TableGenerator() {

        const columns = [
            {
                title: 'Type',
                dataIndex: 'type',
            }, {
                title: 'Time',
                dataIndex: "time"
            }, {
                title: 'Date',
                dataIndex: 'date',
            }, {
                title: 'Price',
                dataIndex: 'price',
            }, {
                title: 'Clinic',
                dataIndex: 'clinic_name',
            }, {
                title: 'Address',
                dataIndex: 'clinic_address',
            }, {
                title: <div style={{float: 'left'}}>Action</div>,
                dataIndex: 'button'
            }
        ];

        const data = []
        this.state.clinics.map((clinic)=> {
            this.props.cart.map((appointment) => {
                if (clinic.id == appointment[3]){
                    data.push({
                    type: appointment[0],
                    time: appointment[2],
                    date: appointment[1],
                    clinic_name: clinic.name,
                    clinic_address: clinic.address,
                    price: '50$',
                    button: <div>
                        <Button type="primary" icon="minus" style={{float: 'left'}} size="large" onClick={() => 
                        this.onRemove(appointment)}>Remove</Button>
                        <Button type="primary" icon="plus" style={{float: 'right'}} size="large" onClick={() => 
                        this.onCheckout(appointment)}>Checkout</Button>
                        </div>
                    })
                }
            });
        })

        return (
            <div>
                <Table columns={columns} dataSource={data} pagination={false}/>
            </div>
        );
    }

    async checkout(){
        let appointment = {hcnumber: this.props.user.hcnumber, length: this.state.length, time:this.state.time , date:this.state.date, clinic_id: this.state.clinic_id }
        console.log("clinic id: " + this.state.clinic_id);
        console.log("appointment object: " + JSON.stringify(appointment));
        fetchAPI("PUT", "/api/appointment/book", appointment).then(
            response => {
              try{
                if (response.success){
                    console.log('it is a success mate')
                    if (this.state.length=='20')
                        this.onRemove(['Checkup', this.state.date, this.state.time, this.state.clinic_id])
                    else
                        this.onRemove(['Annual', this.state.date, this.state.time, this.state.clinic_id])
                    this.setState({alert: false, success: true, annualAlert: false})
                }
                else {
                  console.log('it is a fail mate' + response.message + response.info);
                  if (response.bookableAnnual)
                    this.setState({alert: true, success: false, annualAlert: false})
                  else
                    this.setState({alert: false, success: false, annualAlert: true})
                }
              } catch(e){console.error("Error", e)}
            }
          ).catch((e)=>console.error("Error:", e))
    }

    render() {
        let alert, success, annualAlert;

        if (this.state.alert){
            alert = <div className="flash animated" id="welcome"><Alert bsStyle="warning">Appointment time is not available anymore.</Alert></div>
        }
        else{
            alert = null
        }
          
        if (this.state.success){
            success = <div className="flash animated" id="welcome"><Alert bsStyle="success">Appointment created!</Alert></div>
        }
        else{
            success = null
        }

        if (this.state.annualAlert){
            annualAlert = <div className="flash animated" id="welcome"><Alert bsStyle="warning">It has not been a year since your last annual!</Alert></div>
        }
        else{
            annualAlert = null
        }

        return (
            <div>
                {alert}
                {success}
                {annualAlert}
                <h1>Appointment Cart</h1>
                {this.TableGenerator()}
                <Modal
                    title="Credit Card Information"
                    visible={this.state.visible}
                    onOk={this.handleOk}
                    onCancel={this.handleCancel}
                >
                    Name on card
                    <Input name placeholder="" />
                    <br />
                    Card number
                    <Input placeholder="" />
                    <br />
                    Expiry Date
                    <Input placeholder="" />
                    <br />
                    Security code
                    <Input placeholder="" />
                    <br />
                    Zip/Postal code
                    <Input placeholder="" />
                </Modal>
            </div>
        );
    }
}

function confirmation() {
    message.info('Removed');
}

export default AppointmentCart;