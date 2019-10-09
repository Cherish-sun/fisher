from app.libs.enums import PendingStatus


class DriftViewModel:
    def __init__(self, drift, current_user_id):
        self.drift_id = drift.id
        self.book_title = drift.book_title
        self.book_author = drift.book_author
        self.book_img = drift.book_img
        self.date = drift.create_datetime.strftime('%Y-%m-%d')
        self.message = drift.message
        self.address = drift.address
        self.recipient_name = drift.recipient_name
        self.mobile = drift.mobile
        self.status = drift.pending
        self.you_are = self.requester_or_gifter(drift, current_user_id)
        self.operator = drift.requester_nickname if self.you_are != 'requester' else drift.gifter_nickname
        self.status_str = self.pending_status(drift, self.you_are)

    @staticmethod
    def requester_or_gifter(drift, current_user_id):
        if drift.requester_id == current_user_id:
            you_are = 'requester'
        else:
            you_are = 'gifter'
        return you_are

    @staticmethod
    def pending_status(drift, you_are):
        return PendingStatus.pending_str(drift.pending, you_are)


class DriftCollection:
    def __init__(self, drifts, current_user_id):
        self.data = []
        self.fill(drifts, current_user_id)

    def fill(self, drifts, current_user_id):
        self.data = [DriftViewModel(drift, current_user_id) for drift in drifts]
