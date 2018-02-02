module.exports = (sequelize, DataTypes) => {
    var course = sequelize.define('course', {
        course_id: {
            type: DataTypes.INTEGER,
        },
        faculty_id: {
            type: DataTypes.INTEGER,
        },
        name: {
            type: DataTypes.STRING,
        },
        acronym: {
            type: DataTypes.STRING,
        },
        course_type: {
            type: DataTypes.STRING,
        },
        year: {
            type: DataTypes.INTEGER,
        },
        url: {
            type: DataTypes.STRING(2000),
        },
        plan_url: {
            type: DataTypes.STRING(2000),
        },
    }, {
        tableName: 'course',
        underscored: true,
        timestamps: false,
    });

    course.associate = function(models) {
        models.course.belongsTo(models.faculty);
        models.course.hasMany(models.courseUnit);
    }

    return course;
}