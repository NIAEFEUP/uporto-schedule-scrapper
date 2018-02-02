module.exports = (sequelize, DataTypes) => {
    var schedule = sequelize.define('schedule', {
        day: {
            type: DataTypes.INTEGER(3)
        },
        duration: {
            type: DataTypes.FLOAT(3, 1)
        },
        start_time: {
            type: DataTypes.FLOAT(3, 1)
        },
        location: {
            type: DataTypes.STRING(16)
        },
        lesson_type: {
            type: DataTypes.STRING(3)
        },
        teacher_acronym: {
            type: DataTypes.STRING(16)
        },
        course_unit_id: {
            type: DataTypes.INTEGER(11)
        },
        class_name: {
            type: DataTypes.STRING(16)
        },
        composed_class_name: {
            type: DataTypes.STRING(16)
        }
    }, {
        tableName: 'schedule',
        underscored: true,
        timestamps: false,
    });

    schedule.associate = function(models){
        models.schedule.belongsTo(models.courseUnit);
    }

    return schedule;
}