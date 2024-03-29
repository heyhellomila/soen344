'''
This file documents the api routes for appointment related events.

'''

from flask import Flask, Blueprint, redirect, render_template, url_for, session, request, logging
from index import app
from application.models import Appointment, Doctor, Room, Patient
from application.services import AppointmentService, DoctorScheduleService, RoomScheduleService, RoomService, \
    DoctorService, PatientService
from application.TDG import RoomScheduleTDG
from application.util import *
from passlib.hash import sha256_crypt
from application.util import convertRequestDataToDict as toDict
import json

# This is a Blueprint object. We use this as the object to route certain urls
# In /index.py we import this object and attach it to the Flask object app
# This way all the routes attached to this object will be mapped to app as well.
appointment = Blueprint('appointment', __name__)

# list of possible requests
httpMethods = ['PUT', 'GET', 'POST', 'DELETE']


# Index
@appointment.route('/api/', methods=['GET', 'OPTIONS'])
def index():
    return json.dumps({'success': True, 'status': 'OK', 'message': 'Success'})


@appointment.route('/api/appointment/book', methods=['PUT'])
def newAppointment():
    data = request.data
    data = data.decode('utf8').replace("'", '"')
    data = json.loads(data)
    print(data)
    success = False
    bookableAnnual = None
    message = ""

    patient_hcnumber = data['hcnumber']
    time = data['time']
    date = data['date']
    length = data['length']
    clinic_id = data['clinic_id']

    # to avoid potential double bookings
    patient_is_already_booked = AppointmentService.is_patient_already_booked(
        patient_hcnumber=patient_hcnumber,
        time=time, length=length, clinic_id=clinic_id, date=date)

    if (length is '60'):
        bookableAnnual = PatientService.canBookAnnual(patient_hcnumber)

    if not patient_is_already_booked:
        success = AppointmentService.bookAppointment(patient_hcnumber=patient_hcnumber, clinic_id=clinic_id,
                                                     length=length, time=time,
                                                     date=date)
    if success:
        message = "Appointment has been created"
    else:
        message = "Appointment already exists or there are no doctors/rooms available, or annual cannot be booked."

    response = json.dumps({"success": success, "message": message, "bookableAnnual": bookableAnnual,
                           "patientIsAlreadyBooked": patient_is_already_booked})
    return response


@appointment.route('/api/appointment/book/doctor', methods=['POST'])
def newAppointmentByDoctor():
    message = ""
    success = False
    status_code = 400
    data = toDict(request.data)
    doctor_permit_number = data['permit_number']
    patient_health_card_number = data['hcnumber']
    clinic_id = data['clinic_id']
    date = data['date']
    time = data['time']
    appointment_type = data['appointment_type']
    patientExists = True
    room_is_available = True
    bookable = True
    if appointment_type == 'Annual':
        length = 60
    else:
        length = 20

    # preliminary checks
    if not DoctorService.doctorExists(doctor_permit_number):
        message = "Doctor " + doctor_permit_number + " doesn't exist."
        success = False
        status_code = 404
        response = json.dumps({"success": success, "message": message})
        return response, status_code
    if not PatientService.patientExists(patient_health_card_number):
        message = "Patient " + doctor_permit_number + " doesn't exist."
        patientExists = False
        success = False
        status_code = 404
        response = json.dumps({"success": success, "message": message, "patientExists": patientExists,
                               "room_is_available": room_is_available})
        return response, status_code

    # finding out if the doctor is available
    if appointment_type == 'Annual':
        doctor_is_available = DoctorScheduleService.isDoctorAvailableForAnnual(permit_number=doctor_permit_number,
                                                                               date=date, time=time)
    else:
        doctor_is_available = DoctorScheduleService.isDoctorAvailable(permit_number=doctor_permit_number, date=date,
                                                                      time=time)
    # finding out if a room is avail
    if appointment_type == 'Annual':
        room_is_available = RoomScheduleService.findRoomForAnnual(clinic_id, date, time)
    else:
        room_is_available = RoomScheduleService.findRoomAtTime(clinic_id, date, time)

    # to avoid potential double bookings
    patient_is_already_booked = AppointmentService.is_patient_already_booked(
        patient_hcnumber=patient_health_card_number,
        time=time, length=length, clinic_id=clinic_id, date=date)
    
    # check if annual, if so, check if bookable
    if appointment_type == 'Annual':
        bookable = PatientService.canBookAnnual(patient_health_card_number)

    # booking attempt
    if doctor_is_available and room_is_available and not patient_is_already_booked and bookable:
        AppointmentService.bookAppointmentWithASpecificDoctor(patient_hcnumber=patient_health_card_number,
                                                              doctor_permit_number=doctor_permit_number, length=length,
                                                              time=time, date=date, clinic_id=clinic_id)
        message = "Appointment has been booked successfully"
        success = True
        status_code = 200
        response = json.dumps({"success": success, "message": message, "patientExists": patientExists,
                               "room_is_available": room_is_available,
                               "patientIsAlreadyBooked": patient_is_already_booked})
        return response, status_code
    else:
        message = "Cannot book."
        success = False
        status_code = 200
        response = json.dumps({"success": success, "message": message, "patientExists": patientExists,
                               "room_is_available": room_is_available, "doctor_is_available": doctor_is_available,
                               "patientIsAlreadyBooked": patient_is_already_booked, "bookable": bookable})
        return response, status_code


# Returns an array of appointments consisting of the patient specified
@appointment.route('/api/appointment/check', methods=['GET'])
def checkAppointments():
    data = request.args.get('hcnumber')
    success = False
    message = ""
    appointments = []

    appointments = AppointmentService.getAppointments(data)
    if appointments is not None:
        success = True
    else:
        success = False

    if success:
        message = "Appointment(s) retrieved."
    else:
        message = "No appointment(s) retrieved."

    response = json.dumps({"success": success, "message": message, "appointments": appointments})
    return response


# Returns an array of appointments for doctor specified
@appointment.route('/api/appointment/checkDoctor', methods=['GET'])
def checkAppointmentsDoctor():
    data = request.args.get('doctor_permit_number')
    success = False
    message = ""
    appointments = []

    appointments = AppointmentService.getDoctorAppointments(data)
    if appointments is not None:
        success = True
    else:
        success = False

    if success:
        message = "Appointment(s) retrieved."
    else:
        message = "No appointment(s) retrieved."

    response = json.dumps({"success": success, "message": message, "appointments": appointments})
    return response


@appointment.route('/api/appointment/cancel', methods=['DELETE'])
def cancelAppointment():
    data = request.data
    data = data.decode('utf8').replace("'", '"')
    data = json.loads(data)
    print(data)
    success = False
    cancelled = False
    message = ""

    if AppointmentService.getAppointment(data['id']) is not None:
        success = AppointmentService.cancelAppointment(data['id'])
    if success:
        message = 'Appointment cancelled'
    else:
        message = 'Appointment may not exist or cancellation failed.'

    response = json.dumps({"success": success, "message": message, "cancelled": cancelled})
    return response


@appointment.route('/api/appointment/update/doctor', methods=['PUT'])
def updateAppointmentForDoctor():
    data = request.data
    data = data.decode('utf8').replace("'", '"')
    data = json.loads(data)
    print(data)
    success = False
    message = ""

    if AppointmentService.getAppointment(data['id']) is not None:
        message, success = AppointmentService.updateAppointment(clinic_id=data['clinic_id'],
                                                                appointment_id=data['id'],
                                                                doctor_permit_number=data['permit_number'],
                                                                length=data['length'], new_time=data['time'],
                                                                new_date=data['date'])
    if data['length'] is '60':
        bookableAnnual = PatientService.canBookAnnual(data['hcnumber'])
        response = json.dumps(
            {"success": success, "message": message, "bookableAnnual": bookableAnnual})
    else:
        response = json.dumps(
            {"success": success, "message": message})
    return response


@appointment.route('/api/appointment/update', methods=['PUT'])
def updateAppointment():
    data = request.data
    data = data.decode('utf8').replace("'", '"')
    data = json.loads(data)
    print(data)
    success = False

    if data['length'] is '60':
        bookableAnnual = PatientService.canBookAnnual(data['hcnumber'])

    if AppointmentService.getAppointment(data['id']) is not None:
        success = AppointmentService.updateAppointment(clinic_id=data['clinic_id'],
                                                       appointment_id=data['id'], length=data['length'],
                                                       new_time=data['time'], new_date=data['date'])
    if success:
        message = 'Appointment has been updated.'
        appointment = AppointmentService.getAppointment(data['id'])
    else:
        message = 'Appointment has not been updated.'

    if data['length'] is '60':
        response = json.dumps(
            {"success": success, "message": message, "appointment": appointment, "bookableAnnual": bookableAnnual})
    else:
        response = json.dumps(
            {"success": success, "message": message, "appointment": appointment})
    return response

# /api/appointment/find?date=<insert_date_here>
@appointment.route('/api/appointment/find', methods=['POST'])
def findAppointments():
    data = request.data
    data = data.decode('utf8').replace("'", '"')
    data = json.loads(data)
    date = data['date']
    clinic_id = data['clinic_id']
    message = ""
    success = False
    if (date is None):
        message = 'Enter a date to find the appointments for'
        return message, 404

    availableDoctorPermitNumbers = DoctorScheduleService.getAllAvailableDoctorPermitsByDate(date)
    availableRoomNumbers = RoomService.getAllRoomNumbersByClinic(clinic_id=clinic_id)
    if (availableDoctorPermitNumbers is None):
        message = "Unfortunately there are no doctors available for this date at the moment. Please try later."
        return message, 200
    if (availableRoomNumbers is None):
        message = "Unfortunately there are no rooms available for this date at the moment. Please try later."
        return message, 200
    listOfAvailableAppointments = AppointmentService.crossCheckDoctorAndRoomList(date=date,
                                                                                 doctorPermitNumberList=availableDoctorPermitNumbers,
                                                                                 roomList=availableRoomNumbers,
                                                                                 clinic_id=clinic_id)
    if listOfAvailableAppointments is None:
        return 204
    else:
        success = True
        response = json.dumps(
            {"success": success, "listOfAvailableAppointments": listOfAvailableAppointments, "date": date,
             "message": message})
        return response, 200
