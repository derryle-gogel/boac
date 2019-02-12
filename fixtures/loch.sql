DROP SCHEMA IF EXISTS boac_advising_asc cascade;
DROP SCHEMA IF EXISTS boac_advising_coe cascade;
DROP SCHEMA IF EXISTS boac_advising_notes cascade;
DROP SCHEMA IF EXISTS boac_analytics cascade;
DROP SCHEMA IF EXISTS sis_data cascade;
DROP SCHEMA IF EXISTS student cascade;

CREATE SCHEMA boac_advising_asc;
CREATE SCHEMA boac_advising_coe;
CREATE SCHEMA boac_advising_notes;
CREATE SCHEMA boac_analytics;
CREATE SCHEMA sis_data;
CREATE SCHEMA student;

CREATE TABLE boac_advising_asc.students
(
    sid VARCHAR NOT NULL,
    intensive BOOLEAN NOT NULL,
    active BOOLEAN NOT NULL,
    status_asc VARCHAR,
    group_code VARCHAR,
    group_name VARCHAR,
    team_code VARCHAR,
    team_name VARCHAR
);

CREATE TABLE boac_advising_asc.student_profiles
(
    sid VARCHAR NOT NULL,
    profile TEXT NOT NULL
);

CREATE TABLE boac_advising_coe.students
(
    sid VARCHAR NOT NULL,
    advisor_ldap_uid VARCHAR,
    gender VARCHAR,
    ethnicity VARCHAR,
    minority BOOLEAN NOT NULL,
    did_prep BOOLEAN NOT NULL,
    prep_eligible BOOLEAN NOT NULL,
    did_tprep BOOLEAN NOT NULL,
    tprep_eligible BOOLEAN NOT NULL,
    sat1read INT,
    sat1math INT,
    sat2math INT,
    in_met BOOLEAN NOT NULL,
    grad_term VARCHAR,
    grad_year VARCHAR,
    probation BOOLEAN NOT NULL,
    status VARCHAR
);

CREATE TABLE boac_advising_coe.student_profiles
(
    sid VARCHAR NOT NULL,
    profile TEXT NOT NULL
);

CREATE TABLE boac_advising_notes.advising_notes
(
    id VARCHAR NOT NULL,
    sid VARCHAR NOT NULL,
    advisor_sid VARCHAR,
    appointment_id VARCHAR,
    note_category VARCHAR,
    note_subcategory VARCHAR,
    created_by VARCHAR,
    updated_by VARCHAR,
    note_body TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE boac_analytics.section_mean_gpas
(
    sis_term_id VARCHAR NOT NULL,
    sis_section_id VARCHAR NOT NULL,
    gpa_term_id VARCHAR NOT NULL,
    avg_gpa DOUBLE PRECISION NOT NULL
);

CREATE TABLE sis_data.enrolled_primary_sections
(
    term_id VARCHAR NOT NULL,
    sis_section_id VARCHAR NOT NULL,
    sis_course_name VARCHAR NOT NULL,
    sis_course_name_compressed VARCHAR NOT NULL,
    sis_course_title VARCHAR NOT NULL,
    sis_instruction_format VARCHAR NOT NULL,
    sis_section_num VARCHAR NOT NULL,
    instructors VARCHAR
);

CREATE TABLE sis_data.sis_terms
(
    term_id VARCHAR NOT NULL,
    term_name VARCHAR NOT NULL,
    academic_career VARCHAR NOT NULL,
    term_begins DATE NOT NULL,
    term_ends DATE NOT NULL,
    session_id VARCHAR NOT NULL,
    session_name VARCHAR NOT NULL,
    session_begins DATE NOT NULL,
    session_ends DATE NOT NULL
);

CREATE TABLE student.student_holds
(
    sid VARCHAR NOT NULL,
    feed TEXT NOT NULL
);

CREATE TABLE student.student_profiles
(
    sid VARCHAR NOT NULL,
    profile TEXT NOT NULL
);

CREATE TABLE student.student_academic_status
(
    sid VARCHAR NOT NULL,
    uid VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    level VARCHAR(2),
    gpa DECIMAL(4,3),
    units DECIMAL (4,1)
);

CREATE TABLE student.student_majors
(
    sid VARCHAR NOT NULL,
    major VARCHAR NOT NULL
);

CREATE TABLE student.student_enrollment_terms
(
    sid VARCHAR NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    enrollment_term TEXT NOT NULL
);

CREATE TABLE student.student_term_gpas
(
    sid VARCHAR NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    gpa DECIMAL(4,3),
    units_taken_for_gpa DECIMAL(4,1)
);

INSERT INTO boac_advising_asc.students
(sid, intensive, active, status_asc, group_code, group_name, team_code, team_name)
VALUES
('11667051', TRUE, TRUE, 'Compete', 'WFH', 'Women''s Field Hockey', 'FHW', 'Women''s Field Hockey'),
('11667051', TRUE, TRUE, 'Compete', 'WTE', 'Women''s Tennis', 'TNW', 'Women''s Tennis'),
('8901234567', TRUE, TRUE, 'Compete', NULL, NULL, NULL, NULL),
('2345678901', FALSE, TRUE, 'Compete', 'MFB-DB', 'Football, Defensive Backs', 'FBM', 'Football'),
('2345678901', FALSE, TRUE, 'Compete', 'MFB-DL', 'Football, Defensive Line', 'FBM', 'Football'),
('3456789012', TRUE, TRUE, 'Compete', 'MFB-DL', 'Football, Defensive Line', 'FBM', 'Football'),
('5678901234', FALSE, TRUE, 'Compete', 'MFB-DB', 'Football, Defensive Backs', 'FBM', 'Football'),
('5678901234', FALSE, TRUE, 'Compete', 'MFB-DL', 'Football, Defensive Line', 'FBM', 'Football'),
('5678901234', FALSE, TRUE, 'Compete', 'MTE', 'Men''s Tennis', 'TNM', 'Men''s Tennis'),
('7890123456', TRUE, TRUE, 'Compete', 'MBB', 'Men''s Baseball', 'BAM', 'Men''s Baseball'),
('3456789012', TRUE, TRUE, 'Compete', 'MBB-AA', 'Men''s Baseball', 'BAM', 'Men''s Baseball'),
-- 'A mug is a mug in everything.' - Colonel Harrington
('890127492', TRUE, FALSE, 'Trouble', 'MFB-DB', 'Football, Defensive Backs', 'FBM', 'Football'),
('890127492', TRUE, FALSE, 'Trouble', 'MFB-DL', 'Football, Defensive Line', 'FBM', 'Football'),
('890127492', TRUE, FALSE, 'Trouble', 'MTE', 'Men''s Tennis', 'TNM', 'Men''s Tennis'),
('890127492', TRUE, FALSE, 'Trouble', 'WFH', 'Women''s Field Hockey', 'FHW', 'Women''s Field Hockey'),
('890127492', TRUE, FALSE, 'Trouble', 'WTE', 'Women''s Tennis', 'TNW', 'Women''s Tennis');

INSERT INTO boac_advising_asc.student_profiles
(sid, profile)
VALUES
('11667051', :athletics_profile_11667051),
('2345678901', :athletics_profile_2345678901),
('3456789012', :athletics_profile_3456789012),
('5678901234', :athletics_profile_5678901234),
('7890123456', :athletics_profile_7890123456),
('8901234567', :athletics_profile_8901234567),
('890127492', :athletics_profile_890127492);

INSERT INTO boac_advising_coe.students
(sid, advisor_ldap_uid, gender, ethnicity, minority, did_prep, prep_eligible, did_tprep, tprep_eligible,
  sat1read, sat1math, sat2math, in_met, grad_term, grad_year, probation, status)
VALUES
('11667051', '90412', 'm', 'H', FALSE, TRUE, FALSE, FALSE, FALSE, NULL, NULL, NULL, FALSE, NULL, NULL, FALSE, 'C'),
('7890123456', '1133399', 'f', 'B', TRUE, FALSE, TRUE, FALSE, FALSE, 510, 520, 620, FALSE, 'sp', '2020', FALSE, 'C'),
('9000000000', '1133399', 'f', 'B', TRUE, FALSE, TRUE, FALSE, FALSE, NULL, NULL, 720, FALSE, NULL, NULL, FALSE, 'Z'),
('9100000000', '90412', 'm', 'X', FALSE, FALSE, FALSE, FALSE, TRUE, 720, 760, 770, TRUE, 'fa', '2018', TRUE, 'N');

INSERT INTO boac_advising_coe.student_profiles
(sid, profile)
VALUES
('11667051', :coe_profile_11667051),
('7890123456', :coe_profile_7890123456),
('9000000000', :coe_profile_9000000000),
('9100000000', :coe_profile_9100000000);

INSERT INTO boac_advising_notes.advising_notes
(id, sid, note_body, created_at, updated_at)
VALUES
('11667051-00001', '11667051', 'Brigitte is making athletic and moral progress', '2017-10-31T12:00:00Z', '2017-10-31T12:00:00Z'),
('11667051-00002', '11667051', 'Brigitte demonstrates a cavalier attitude toward university requirements', '2017-11-01T12:00:00Z', '2017-11-01T12:00:00Z'),
('9000000000-00001', '9000000000', 'Is this student even on campus?', '2017-11-02T12:00:00Z', '2017-11-02T12:00:00Z');

INSERT INTO boac_analytics.section_mean_gpas
(sis_term_id, sis_section_id, gpa_term_id, avg_gpa)
VALUES
('2178','90100','cumulative',3.302),
('2178','90100','2175',3.12),
('2178','90100','2172',3.445),
('2178','90200','cumulative',3.131),
('2178','90200','2175',3.055),
('2178','90200','2172',3.23);

INSERT INTO sis_data.enrolled_primary_sections
(term_id, sis_section_id, sis_course_name, sis_course_name_compressed, sis_course_title, sis_instruction_format, sis_section_num, instructors)
VALUES
('2172', '22100', 'MATH 1A', 'MATH1A', 'Calculus', 'LEC', '001', 'Gottfried Wilhelm Leibniz'),
('2178', '21057', 'DANISH 1A', 'DANISH1A', 'Beginning Danish', 'LEC', '001', 'Karen Blixen'),
('2178', '22140', 'MATH 1A', 'MATH1A', 'Calculus', 'LEC', '001', 'Gottfried Wilhelm Leibniz'),
('2178', '22141', 'MATH 1A', 'MATH1A', 'Calculus', 'LEC', '002', 'Sir Isaac Newton'),
('2178', '22172', 'MATH 16A', 'MATH16A', 'Analytic Geometry and Calculus', 'LEC', '001', 'Gottfried Wilhelm Leibniz, Sir Isaac Newton'),
('2178', '22173', 'MATH 16A', 'MATH16A', 'Analytic Geometry and Calculus', 'LEC', '002', 'Gottfried Wilhelm Leibniz'),
('2178', '22174', 'MATH 16B', 'MATH16B', 'Analytic Geometry and Calculus', 'LEC', '001', 'Sir Isaac Newton'),
('2178', '22460', 'MATH 185', 'MATH185', 'Introduction to Complex Analysis', 'LEC', '001', 'Leonhard Euler'),
('2178', '22114', 'MATH 55', 'MATH55', 'Discrete Mathematics', 'LEC', '001', 'David Hilbert');

INSERT INTO sis_data.sis_terms
(term_id, term_name, academic_career, term_begins, term_ends, session_id, session_name, session_begins, session_ends)
VALUES
('2188', '2018 Fall', 'LAW', '2018-08-13', '2018-12-17', '1', 'Regular Academic Session', '2018-08-20', '2018-12-05'),
('2188', '2018 Fall', 'GRAD', '2018-08-15', '2018-12-14', '1', 'Regular Academic Session', '2018-08-22', '2018-12-07'),
('2188', '2018 Fall', 'UCBX', '2018-08-15', '2018-12-14', '1', 'Regular Academic Session', '2018-08-22', '2018-12-07'),
('2188', '2018 Fall', 'UGRD', '2018-08-15', '2018-12-14', '1', 'Regular Academic Session', '2018-08-22', '2018-12-07'),
('2185', '2018 Summer', 'LAW', '2018-05-14', '2018-08-13', '10W', '10 Week', '2018-05-15', '2018-07-19'),
('2185', '2018 Summer', 'LAW', '2018-05-14', '2018-08-13', 'Q1', 'Summer LLM First Quarter', '2018-05-15', '2018-06-04'),
('2185', '2018 Summer', 'LAW', '2018-05-14', '2018-08-13', 'Q2', 'Summer LLM Second Quarter', '2018-06-06', '2018-06-22'),
('2185', '2018 Summer', 'LAW', '2018-05-14', '2018-08-13', 'Q3', 'Summer LLM Third Quarter', '2018-06-27', '2018-07-19'),
('2185', '2018 Summer', 'LAW', '2018-05-14', '2018-08-13', 'Q4', 'Summer LLM Fourth Quarter', '2018-07-24', '2018-08-13'),
('2185', '2018 Summer', 'GRAD', '2018-05-21', '2018-08-10', '1', 'Regular Academic Session', '2018-05-21', '2018-08-10'),
('2185', '2018 Summer', 'GRAD', '2018-05-21', '2018-08-10', '10W', '10 Week', '2018-06-04', '2018-08-10'),
('2185', '2018 Summer', 'GRAD', '2018-05-21', '2018-08-10', '3W', 'Session E', '2018-07-23', '2018-08-10'),
('2185', '2018 Summer', 'GRAD', '2018-05-21', '2018-08-10', '6W1', 'Six Week - First', '2018-05-21', '2018-06-29'),
('2185', '2018 Summer', 'GRAD', '2018-05-21', '2018-08-10', '6W2', 'Six Week - Second', '2018-07-02', '2018-08-10'),
('2185', '2018 Summer', 'GRAD', '2018-05-21', '2018-08-10', '8W', 'Session C', '2018-06-18', '2018-08-10'),
('2185', '2018 Summer', 'UGRD', '2018-05-21', '2018-08-10', '1', 'Regular Academic Session', '2018-05-21', '2018-08-10'),
('2185', '2018 Summer', 'UGRD', '2018-05-21', '2018-08-10', '10W', '10 Week', '2018-06-04', '2018-08-10'),
('2185', '2018 Summer', 'UGRD', '2018-05-21', '2018-08-10', '3W', 'Session E', '2018-07-23', '2018-08-10'),
('2185', '2018 Summer', 'UGRD', '2018-05-21', '2018-08-10', '6W1', 'Six Week - First', '2018-05-21', '2018-06-29'),
('2185', '2018 Summer', 'UGRD', '2018-05-21', '2018-08-10', '6W2', 'Six Week - Second', '2018-07-02', '2018-08-10'),
('2185', '2018 Summer', 'UGRD', '2018-05-21', '2018-08-10', '8W', 'Session C', '2018-06-18', '2018-08-10'),
('2182', '2018 Spring', 'LAW', '2018-01-01', '2018-05-09', '1', 'Regular Academic Session', '2018-01-08', '2018-04-20'),
('2182', '2018 Spring', 'GRAD', '2018-01-09', '2018-05-11', '1', 'Regular Academic Session', '2018-01-16', '2018-05-04'),
('2182', '2018 Spring', 'UCBX', '2018-01-09', '2018-05-11', '1', 'Regular Academic Session', '2018-01-16', '2018-05-04'),
('2182', '2018 Spring', 'UGRD', '2018-01-09', '2018-05-11', '1', 'Regular Academic Session', '2018-01-16', '2018-05-04'),
('2178', '2017 Fall', 'LAW', '2017-08-14', '2017-12-15', '1', 'Regular Academic Session', '2017-08-21', '2017-12-05'),
('2178', '2017 Fall', 'GRAD', '2017-08-16', '2017-12-15', '1', 'Regular Academic Session', '2017-08-23', '2017-12-08'),
('2178', '2017 Fall', 'UCBX', '2017-08-16', '2017-12-15', '1', 'Regular Academic Session', '2017-08-23', '2017-12-08'),
('2178', '2017 Fall', 'UGRD', '2017-08-16', '2017-12-15', '1', 'Regular Academic Session', '2017-08-23', '2017-12-08'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', '1', 'Regular Academic Session', '2017-05-22', '2017-08-11'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', '10W', '10 Week', '2017-06-05', '2017-08-11'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', '3W', 'Session E', '2017-07-17', '2017-08-04'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', '6W1', 'Six Week - First', '2017-05-22', '2017-06-30'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', '6W2', 'Six Week - Second', '2017-07-03', '2017-08-11'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', '8W', 'Session C', '2017-06-19', '2017-08-11'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', 'Q1', 'Summer LLM First Quarter', '2017-05-22', '2017-06-13'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', 'Q2', 'Summer LLM Second Quarter', '2017-06-14', '2017-07-04'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', 'Q3', 'Summer LLM Third Quarter', '2017-07-05', '2017-07-25'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', 'Q4', 'Summer LLM Fourth Quarter', '2017-07-26', '2017-08-15'),
('2175', '2017 Summer', 'GRAD', '2017-05-22', '2017-08-11', '1', 'Regular Academic Session', '2017-05-22', '2017-08-11'),
('2175', '2017 Summer', 'GRAD', '2017-05-22', '2017-08-11', '10W', '10 Week', '2017-06-05', '2017-08-11'),
('2175', '2017 Summer', 'GRAD', '2017-05-22', '2017-08-11', '3W', 'Session E', '2017-07-17', '2017-08-04'),
('2175', '2017 Summer', 'GRAD', '2017-05-22', '2017-08-11', '6W1', 'Six Week - First', '2017-05-22', '2017-06-30'),
('2175', '2017 Summer', 'GRAD', '2017-05-22', '2017-08-11', '6W2', 'Six Week - Second', '2017-07-03', '2017-08-11'),
('2175', '2017 Summer', 'GRAD', '2017-05-22', '2017-08-11', '8W', 'Session C', '2017-06-19', '2017-08-11'),
('2175', '2017 Summer', 'UGRD', '2017-05-22', '2017-08-11', '1', 'Regular Academic Session', '2017-05-22', '2017-08-11'),
('2175', '2017 Summer', 'UGRD', '2017-05-22', '2017-08-11', '10W', '10 Week', '2017-06-05', '2017-08-11'),
('2175', '2017 Summer', 'UGRD', '2017-05-22', '2017-08-11', '3W', 'Session E', '2017-07-17', '2017-08-04'),
('2175', '2017 Summer', 'UGRD', '2017-05-22', '2017-08-11', '6W1', 'Six Week - First', '2017-05-22', '2017-06-30'),
('2175', '2017 Summer', 'UGRD', '2017-05-22', '2017-08-11', '6W2', 'Six Week - Second', '2017-07-03', '2017-08-11'),
('2175', '2017 Summer', 'UGRD', '2017-05-22', '2017-08-11', '8W', 'Session C', '2017-06-19', '2017-08-11'),
('2172', '2017 Spring', 'LAW', '2017-01-02', '2017-05-10', '1', 'Regular Academic Session', '2017-01-09', '2017-04-25'),
('2172', '2017 Spring', 'GRAD', '2017-01-10', '2017-05-12', '1', 'Regular Academic Session', '2017-01-17', '2017-05-05'),
('2172', '2017 Spring', 'UCBX', '2017-01-10', '2017-05-12', '1', 'Regular Academic Session', '2017-01-17', '2017-05-05'),
('2172', '2017 Spring', 'UGRD', '2017-01-10', '2017-05-12', '1', 'Regular Academic Session', '2017-01-17', '2017-05-05'),
('2168', '2016 Fall', 'LAW', '2016-08-15', '2016-12-15', '1', 'Regular Academic Session', '2016-08-22', '2016-12-15'),
('2168', '2016 Fall', 'GRAD', '2016-08-17', '2016-12-16', '1', 'Regular Academic Session', '2016-08-24', '2016-12-09'),
('2168', '2016 Fall', 'UCBX', '2016-08-17', '2016-12-16', '1', 'Regular Academic Session', '2016-08-24', '2016-12-09'),
('2168', '2016 Fall', 'UGRD', '2016-08-17', '2016-12-16', '1', 'Regular Academic Session', '2016-08-24', '2016-12-09');

INSERT INTO student.student_holds
(sid, feed)
VALUES
('5678901234', :holds_5678901234_S01),
('5678901234', :holds_5678901234_V00);

INSERT INTO student.student_profiles
(sid, profile)
VALUES
('11667051', :profile_11667051),
('2345678901', :profile_2345678901),
('3456789012', :profile_3456789012),
('5678901234', :profile_5678901234),
('7890123456', :profile_7890123456),
('8901234567', :profile_8901234567),
('890127492', :profile_890127492),
('9000000000', :profile_9000000000),
('9100000000', :profile_9100000000);

INSERT INTO student.student_academic_status
(sid, uid, first_name, last_name, level, gpa, units)
VALUES
('11667051', '61889', 'Deborah', 'Davies', NULL, NULL, 0),
('2345678901', '98765', 'Dave', 'Doolittle', '30', 3.495, 34),
('3456789012', '242881', 'Paul', 'Kerschen', '30', 3.005, 70),
('5678901234', '9933311', 'Sandeep', 'Jayaprakash', '40', 3.501, 102),
('7890123456', '1049291', 'Paul', 'Farestveit', '40', 3.9, 110),
('8901234567', '123456', 'John David', 'Crossman', '10', 1.85, 12),
('890127492', '211159', 'Siegfried', 'Schlemiel', '20', 0.4, 8),
('9000000000', '300847', 'Wolfgang', 'Pauli', '20', 2.3, 55),
('9100000000', '300848', 'Nora Stanton', 'Barney', '20', 3.85, 60);

INSERT INTO student.student_majors
(sid, major)
VALUES
('11667051', 'English BA'),
('11667051', 'Nuclear Engineering BS'),
('2345678901', 'Chemistry BS'),
('3456789012', 'English BA'),
('3456789012', 'Political Economy BA'),
('5678901234', 'Letters & Sci Undeclared UG'),
('7890123456', 'Nuclear Engineering BS'),
('8901234567', 'Economics BA'),
('890127492', 'Mathematics'),
('9000000000', 'Engineering Undeclared UG'),
('9100000000', 'Engineering Undeclared UG');

INSERT INTO student.student_enrollment_terms
(sid, term_id, enrollment_term)
VALUES
('11667051', '2162', :enrollment_term_11667051_2162),
('11667051', '2172', :enrollment_term_11667051_2172),
('11667051', '2178', :enrollment_term_11667051_2178),
('11667051', '2182', :enrollment_term_11667051_2182),
('2345678901', '2172', :enrollment_term_2345678901_2172),
('3456789012', '2178', :enrollment_term_3456789012_2178),
('5678901234', '2178', :enrollment_term_5678901234_2178);

INSERT INTO student.student_term_gpas
(sid, term_id, gpa, units_taken_for_gpa)
VALUES
('11667051', '2162', 3.8, 15),
('11667051', '2172', 2.7, 17),
('11667051', '2175', 0, 0),
('11667051', '2178', 1.8, 15),
('11667051', '2182', 2.9, 14),
('2345678901', '2172', 3.5, 16),
('2345678901', '2175', 0, 4),
('3456789012', '2178', 3.2, 15),
('5678901234', '2178', 2.1, 14);
