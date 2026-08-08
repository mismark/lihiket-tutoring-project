this is a descriptions about the project
online_tutoring

| URL                                            | Purpose                     |
| ---------------------------------------------- | --------------------------- |
| `http://127.0.0.1:8000/`                       | Home page                   |
| `http://127.0.0.1:8000/dashboard/`             | Dashboard                   |
| `http://127.0.0.1:8000/accounts/register/`     | Register                    |
| `http://127.0.0.1:8000/accounts/login/`        | Login                       |
| `http://127.0.0.1:8000/accounts/profile/`      | User Profile                |
| `http://127.0.0.1:8000/accounts/edit-profile/` | Edit Profile                |
| `http://127.0.0.1:8000/courses/`               | Course List                 |
| `http://127.0.0.1:8000/courses/create/`        | Create Course               |
| `http://127.0.0.1:8000/courses/1/`             | Course Detail (Course ID 1) |
| `http://127.0.0.1:8000/courses/1/update/`      | Update Course               |
| `http://127.0.0.1:8000/courses/1/delete/`      | Delete Course               |
| `http://127.0.0.1:8000/admin/`                 | Django Admin                |


<!-- to see all urls for my projects  -->


C:\Users\HP\online_tutoring>venv\scripts\activate

(venv) C:\Users\HP\online_tutoring>python manage.py show_urls
/       apps.accounts.views.home        home
/accounts/      apps.accounts.views.home        accounts:home
/accounts/edit-profile/ apps.accounts.views.edit_profile        accounts:edit_profile
/accounts/forgot-password/      django.contrib.auth.views.PasswordResetViewaccounts:forgot_password
/accounts/login/        apps.accounts.views.login_view  accounts:login
/accounts/logout/       apps.accounts.views.logout_view accounts:logout
/accounts/password-reset/done/  django.contrib.auth.views.PasswordResetDoneView     accounts:password_reset_done
/accounts/profile/      apps.accounts.views.profile_view        accounts:profile
/accounts/register/     apps.accounts.views.register_view       accounts:register
/accounts/reset/<uidb64>/<token>/       django.contrib.auth.views.PasswordResetConfirmView  accounts:password_reset_confirm
/accounts/reset/done/   django.contrib.auth.views.PasswordResetCompleteViewaccounts:password_reset_complete
/admin/ django.contrib.admin.sites.index        admin:index
/admin/<app_label>/     django.contrib.admin.sites.app_index    admin:app_list
/admin/<url>    django.contrib.admin.sites.catch_all_view
/admin/accounts/user/   django.contrib.admin.options.changelist_view    admin:accounts_user_changelist
/admin/accounts/user/<id>/password/     django.contrib.auth.admin.user_change_password      admin:auth_user_password_change
/admin/accounts/user/<path:object_id>/  django.views.generic.base.RedirectView
/admin/accounts/user/<path:object_id>/change/   django.contrib.admin.options.change_view    admin:accounts_user_change
/admin/accounts/user/<path:object_id>/delete/   django.contrib.admin.options.delete_view    admin:accounts_user_delete
/admin/accounts/user/<path:object_id>/history/  django.contrib.admin.options.history_view   admin:accounts_user_history
/admin/accounts/user/add/       django.contrib.auth.admin.add_view      admin:accounts_user_add
/admin/auth/group/      django.contrib.admin.options.changelist_view    admin:auth_group_changelist
/admin/auth/group/<path:object_id>/     django.views.generic.base.RedirectView
/admin/auth/group/<path:object_id>/change/      django.contrib.admin.options.change_view    admin:auth_group_change
/admin/auth/group/<path:object_id>/delete/      django.contrib.admin.options.delete_view    admin:auth_group_delete
/admin/auth/group/<path:object_id>/history/     django.contrib.admin.options.history_view   admin:auth_group_history
/admin/auth/group/add/  django.contrib.admin.options.add_view   admin:auth_group_add
/admin/autocomplete/    django.contrib.admin.sites.autocomplete_view    admin:autocomplete
/admin/courses/course/  django.contrib.admin.options.changelist_view    admin:courses_course_changelist
/admin/courses/course/<path:object_id>/ django.views.generic.base.RedirectView
/admin/courses/course/<path:object_id>/change/  django.contrib.admin.options.change_view    admin:courses_course_change
/admin/courses/course/<path:object_id>/delete/  django.contrib.admin.options.delete_view    admin:courses_course_delete
/admin/courses/course/<path:object_id>/history/ django.contrib.admin.options.history_view   admin:courses_course_history
/admin/courses/course/add/      django.contrib.admin.options.add_view   admin:courses_course_add
/admin/courses/courseprogress/  django.contrib.admin.options.changelist_viewadmin:courses_courseprogress_changelist
/admin/courses/courseprogress/<path:object_id>/ django.views.generic.base.RedirectView
/admin/courses/courseprogress/<path:object_id>/change/  django.contrib.admin.options.change_view    admin:courses_courseprogress_change
/admin/courses/courseprogress/<path:object_id>/delete/  django.contrib.admin.options.delete_view    admin:courses_courseprogress_delete
/admin/courses/courseprogress/<path:object_id>/history/ django.contrib.admin.options.history_view   admin:courses_courseprogress_history
/admin/courses/courseprogress/add/      django.contrib.admin.options.add_view       admin:courses_courseprogress_add
/admin/courses/enrollment/      django.contrib.admin.options.changelist_viewadmin:courses_enrollment_changelist
/admin/courses/enrollment/<path:object_id>/     django.views.generic.base.RedirectView
/admin/courses/enrollment/<path:object_id>/change/      django.contrib.admin.options.change_view    admin:courses_enrollment_change
/admin/courses/enrollment/<path:object_id>/delete/      django.contrib.admin.options.delete_view    admin:courses_enrollment_delete
/admin/courses/enrollment/<path:object_id>/history/     django.contrib.admin.options.history_view   admin:courses_enrollment_history
/admin/courses/enrollment/add/  django.contrib.admin.options.add_view   admin:courses_enrollment_add
/admin/jsi18n/  django.contrib.admin.sites.i18n_javascript      admin:jsi18n
/admin/login/   django.contrib.admin.sites.login        admin:login
/admin/logout/  django.contrib.admin.sites.logout       admin:logout
/admin/password_change/ django.contrib.admin.sites.password_change      admin:password_change
/admin/password_change/done/    django.contrib.admin.sites.password_change_done     admin:password_change_done
/admin/r/<path:content_type_id>/<path:object_id>/       django.contrib.contenttypes.views.shortcut  admin:view_on_site
/courses/       apps.courses.views.course_list  courses:course_list
/courses/<int:pk>/      apps.courses.views.course_detail        courses:course_detail
/courses/<int:pk>/delete/       apps.courses.views.course_delete        courses:course_delete
/courses/<int:pk>/enroll/       apps.courses.views.enroll_course        courses:enroll_course
/courses/<int:pk>/progress/     apps.courses.views.update_progress      courses:update_progress
/courses/<int:pk>/update/       apps.courses.views.course_update        courses:course_update
/courses/create/        apps.courses.views.course_create        courses:course_create
/courses/my-courses/    apps.courses.views.my_courses   courses:my_courses
/courses/my-courses/    apps.courses.views.my_courses   courses:my_courses
/dashboard/     apps.dashboard.views.home       dashboard:home
/media/<path>   django.views.static.serve
